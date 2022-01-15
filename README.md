# Social Media Backend System(Twitter)

Tech Stack: Python, Django, MySQL, HBase, Redis, Memcached, Amazon S3.

Used Redis and Memcached to reduce db queries for tables which has lot reads and less writes.

Used Key-value store HBase to split db queries for tables which has less reads and lot writes.

Used denormalization to store the number of comments & likes in order to reduce db queries.

Used Message Queue to deliver asynchronized tasks to reduce response time.
