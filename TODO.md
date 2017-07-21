# features
* creates a new record in airtable from email based on trigger phrase

* links record to person based on email address

* creates new record for person if email address not found

# structure
* bring down new emails if they exist __DONE!__
* parse emails for specific trigger text, __DONE!__ if found, mark as read and continue,
  otherwise stop NOTE: need to move marking as read to after conditional regex
  search. Either make email global object or put flow control in the reading.

* query airtable api (with http get request: curl or similar python)
  (caching?) to get copy of second table with the records to search. __DONE!__

* search records (some code a scratch file) for email addresses matching To
  retrieved from email. If no record exists, create one from email header
  data. either way, return 'id' field of record for linking. NOTE: write
  function for generating curl calls early. __DONE__

* assemble new record with parsed data into json notation, upload to
  at __DONE!__

* send email if record fails to create, general error handling



