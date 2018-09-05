import re
import smtplib
import dns.resolver
from flask import Flask, render_template, request, url_for, redirect, flash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'random'


@app.route('/')
def index():
    return render_template('email.html')

# port defines the port used by the api server


@app.route('/result', methods=['POST', 'GET'])
def result():
    if request.method == 'POST':
        inputAddress = request.form['emailadd']
        fromAddress = 'corn@bt.com'

    # Simple Regex for syntax checking

        regex = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
        addressToVerify = str(inputAddress.lower())
        match = re.match(regex, addressToVerify)

        # Syntax check
        match = re.match(regex, addressToVerify)
        if match is None:
            return render_template('invalid.html', invalid="Invalid Email")

        # Get domain for DNS lookup
        splitAddress = addressToVerify.split('@')
        domain = str(splitAddress[1])
        # MX record lookup
        records = dns.resolver.query(domain, 'MX')
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)

        # SMTP lib setup (use debug level for full output)
        server = smtplib.SMTP()
        server.set_debuglevel(0)

        # SMTP Conversation
        server.connect(mxRecord)

        # server.local_hostname(Get local server hostname)
        server.helo(server.local_hostname)
        server.mail(fromAddress)
        code, message = server.rcpt(str(addressToVerify))
        if code == 250:
            valid = "Email is valid"
            return render_template('valid.html', valid=valid, domain=domain)

        elif code == 421:
            return render_template('invalid.html', invalid="The mail server will be shut down. Save the mail message and try again later.")
        elif code == 450:
            return render_template('invalid.html', invalid="The mailbox that you are trying to reach is busy. Wait a little while and try again.")
        elif code == 451:
            return render_template('invalid.html', invalid="The requested action was not done. Some error occurmiles in the mail server.")
        elif code == 452:
            return render_template('invalid.html', invalid="The requested action was not done. The mail server ran out of system storage.")
        elif code == 503:
            return render_template('invalid.html', invalid="The last command was sent out of sequence. For example, you might have sent DATA before sending RECV.")
        elif code == 550:
            return render_template('invalid.html', invalid="The mailbox that you are trying to reach can't be found or you don't have access rights.")
        elif code == 551:
            return render_template('invalid.html', invalid="The specified user is not local; part of the text of the message will contain a forwarding address.")
        elif code == 552:
            return render_template('invalid.html', invalid="The mailbox that you are trying to reach has run out of space. Store the message and try again tomorrow or in a few days-after the user gets a chance to delete some messages.")
        elif code == 553:
            return render_template('invalid.html', invalid="The mail address that you specified was not syntactically correct.")
        elif code == 554:
            return render_template('invalid.html', invalid="The mail transaction has failed for unknown causes.")
        if code != 250:
            return render_template('invalid.html', invalid="invalid email")


def randomEmail(domain):
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    result = []
    for i in range(20):
        result[i] = chars[random.randint(len(chars))]

    return (str(result), domain)
if __name__ == '__main__':
    app.run(debug=True)
