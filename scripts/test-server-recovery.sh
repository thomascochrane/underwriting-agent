#!/usr/bin/env bash
# Isolated crash test: no credentials, model calls, Telegram sends, or live inputs.
set -euo pipefail
cd "$(dirname "$0")/.."
image=$(sed -n 's/^UNDERWRITER_IMAGE=//p' engine.env)
test_root=$(mktemp -d /tmp/underwriting-recovery.XXXXXX)
test_name="underwriting-recovery-${test_root##*.}"
trap 'docker rm -f "$test_name" >/dev/null 2>&1 || true' EXIT
cat > "$test_root/fake-engine.py" <<'PY'
#!/opt/engine-venv/bin/python
import time
time.sleep(120)
PY
printf 'synthetic crash-test input' > "$test_root/tape.xlsx"
chmod 755 "$test_root" "$test_root/fake-engine.py"
chown -R 10000:10000 "$test_root"
docker run --rm --entrypoint /opt/engine-venv/bin/python \
  -e UNDERWRITER_INPUT_ROOTS=/jobs -v "$test_root:/jobs" -v "$PWD/deployment:/deployment:ro" \
  "$image" /deployment/jobs/client.py submit /jobs/tape.xlsx --asset-class mca \
  --request-key crash-test --no-ai --offline > "$test_root/submission.json"
docker run -d --name "$test_name" --init --memory 256m --cpus 0.5 \
  -e UNDERWRITER_CLI=/jobs/fake-engine.py -v "$test_root:/jobs" -v "$PWD/deployment:/deployment:ro" \
  "$image" >/dev/null
read_state() {
  python3 - "$test_root/jobs.sqlite3" <<'PY'
import sqlite3, sys
with sqlite3.connect(sys.argv[1]) as db:
    print(db.execute('SELECT state FROM jobs').fetchone()[0])
PY
}
for attempt in $(seq 1 30); do
  [[ $(read_state) == running ]] && break
  sleep 1
done
[[ $(read_state) == running ]]
docker kill --signal KILL "$test_name" >/dev/null
docker start "$test_name" >/dev/null
for attempt in $(seq 1 30); do
  [[ $(read_state) == interrupted ]] && break
  sleep 1
done
[[ $(read_state) == interrupted ]]
printf 'PASS: a killed worker recovered its running job as interrupted without rerunning it. Evidence: %s\n' "$test_root"
