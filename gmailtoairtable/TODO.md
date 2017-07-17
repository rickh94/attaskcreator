# features
* creates a new record in airtable from email based on trigger phrase

* links record to person based on email address

* creates new record for person if email address not found

# structure
* bring down new emails if they exist DONE!
* parse emails for specific trigger text, if found, mark as read and continue,
  otherwise stop NOTE: need to move marking as read to after conditional regex
  search. Either make email global object or put flow control in the reading.

* query airtable api (with http get request: curl or similar python)
  (caching?) to get copy of second table with the records to search.

* search records for email addresses matching To retrieved from email. If no
  record exists, create one from email header data. either way, return 'id'
  field of record for linking. NOTE: write function for generating curl calls
  early. 

* assemble new record with parsed data into json notation

* build curl command to create record in the table.

* call curl, get return code to reattempt if fails.

* send email if record fails after X tries.



