import argparse
import getpass
import imaplib
import email
from email.header import decode_header, make_header


def print_email_info(server, user, password, ssl, email_range):
    if ssl:
        server = imaplib.IMAP4_SSL(server)
    else:
        server = imaplib.IMAP4(server)

    server.login(user, password)
    server.select("INBOX")

    if email_range:
        num_start, num_end = email_range
    else:
        num_start = 1
        num_end = server.select("INBOX")[1][0].decode()

    for num in range(int(num_start), int(num_end) + 1):
        _, data = server.fetch(str(num), "(RFC822)")
        raw_email = data[0][1]
        msg = email.message_from_bytes(raw_email)

        subject = make_header(decode_header(msg["Subject"])).__str__()
        from_ = make_header(decode_header(msg["From"])).__str__()
        to = make_header(decode_header(msg["To"])).__str__()
        date = msg["Date"]
        size = len(raw_email)

        attachments = [
            (part.get_filename(),
             part.get("Content-Disposition").split("size=")[1])
            for part in msg.walk()
            if part.get_content_maintype() == "multipart"
        ]

        print(
            f"From: {from_}\nTo: {to}\nSubject: {subject}\nDate: {date}\nSize: {size} bytes\nAttachments: {len(attachments)}")
        for name, size in attachments:
            print(f"  {name} ({size} bytes)")
        print("-" * 80)

    server.logout()


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and display email information.")

    parser.add_argument("--ssl", action="store_true",
                        help="use SSL if the server supports it (default is not to use)")
    parser.add_argument("-s", "--server", required=True,
                        help="IMAP server address in the format address[:port] (default port is 143)")
    parser.add_argument("-n", nargs="*", help="email range (default is all)")
    parser.add_argument("-u", "--user", required=True, help="username")

    args = parser.parse_args()

    password = getpass.getpass(prompt="Password: ", stream=None)

    if ":" in args.server:
        server, port = args.server.split(":")
        server = ":".join((args.server, port))
    else:
        server = ":".join((args.server, "993"))
    print(server)

    email_range = tuple(map(int, args.n)) if args.n else None

    print_email_info(server, args.user, password, args.ssl, email_range)


if __name__ == "__main__":
    main()
