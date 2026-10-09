# Email connection (deferred)

No inbox is connected and this deployment does not send email.

Hermes has two different email capabilities:
- An email gateway: an allowed sender emails the assistant and receives an in-thread reply.
- Email tools/skills: the assistant can manage a mailbox or draft/send messages during other tasks.

The requested future use is the first. Configure it later through
`hermes gateway setup` in the maintenance shell, using a dedicated agent mailbox,
supported IMAP/SMTP authentication, and an explicit sender allowlist. Check the
mail provider's authentication requirements before choosing a mailbox.

The gateway is an active reply service, not an inbox-only reader. Connect only when
automatic replies to the approved senders are intended. Sending lender outreach
is a separate capability and is not enabled by this base deployment.

No inbound ports are needed for an IMAP polling connection. Keep credentials in
the Docker state volume. Do not place them in versioned YAML or Markdown files.

The current startup check requires Telegram because it is the first channel.
If email becomes the only channel, update and test the check at that time.

[Official email gateway documentation](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/email)