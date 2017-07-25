# Airtable Task Creator
Creates entries in an Airtable 'Tasks' table linked to people in a people
table from emails sent to those people (and copied to a burner email account).
If the email address is not in the table, a new record will be created for
that person.

## Installation
The simplest way to install is to run `sudo python install.py`.

You can install with some options to get some extras

| Argument | Description |
|----------|-------------|
| -h, --help | show this help message and exit. |
| -p INSTALL_PREFIX, --install-prefix INSTALL_PREFIX | Specify alternate installation prefix|
| -s, --install-units | Install systemd service and timer from [extras](extras) |
| -c CONFIG_FILE, --config-file CONFIG_FILE | Specify a configuration file |
| --make-config | Interactively generate config file |

## Usage
This is most useful when automated in some way. Systemd units are included.
All options are in the configuration file so simply run the script
periodically.

## Configuration
An example configuration file is included. The can be copied and modified and installed
with -c, or one created interactively with --make-config. The example will be copied 
to `/etc/attaskcreator` for future reference.
Fields are as follows:

[Email]

__User:__ burner email to retrieve emails from

__Password:__ password for the burner email. You should enable two factor and
generate an app password because it will be stored in plain text. Also do not
run this on from a server you do not fully control.

__IMAP URL:__ url for imap retrieval of burner email

__SMTP URL:__ url for smtp sending from burner email

__Error Email:__ your email to send a message to if a record is not created.


[Airtable]

__API Key:__ The api key for the database you want to use. (See the
[Airtable Documentation](http://airtable.com/api) for more information.)

__Database ID:__ The database id for the database you want to use. This is the
part of the api url after /v0/.

[AWS]

__Access Key ID:__ Api access key id for uploading attachments temporarily to
s3

__Secret Access Key:__ Secret key for uploading attachments temporarily to s3

__Bucket:__ Bucket for uploading attachments temporarily.

Airtable can only accept files in the form of urls to download. Current
implementation uploads attachments to s3 and generates a pre-signed url for
Airtable to use. It is recommended to configure an AWS user that has access
only to the bucket used for this and expire the objects in that bucket very
quickly.


[Tasks Table]

This is the table that new records will be inserted into

__Name:__ the name of the table

__People Link Field:__ The field that is linked to the people table

__Attachment Link Field:__ The field that is linked to the files table

__Text Field:__ The field where the parsed text will be inserted

__Notes Field:__ Optionally the full text of the email can be inserted into
this field, leave out to not do this.


[People Table]

This is the table with all the people in it.

__Name:__ the name of the table

__Email Field:__ The field containing the email addresses


[Files Table]

This is the table that will have attachments uploaded to it.

__Name:__ the name of the table.

__Key Field:__ the primary key for the table.

__Attachment Field:__ The field where the actual attachments will be uploaded.


[Parse]

__Trigger Phrase:__ This is the prefix to the text that will be grabbed from
the email. Everything after this will be grabbed for the __Text Field__ in the
Tasks Table up to the __Termination Character__.

__Termination Character:__ see above.

