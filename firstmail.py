import smtplib, ssl

port = 465  # For SSL
password = "jNcpWXrYpG85T3w"

# Create a secure SSL context
context = ssl.create_default_context()

with smtplib.SMTP_SSL("smtp.gmail.com", port) as server:
    server.login("Der.Weg.ins.All.Passwort@gmail.com", password)
    # TODO: Send email here