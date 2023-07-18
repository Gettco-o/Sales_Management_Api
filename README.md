The sales management api was developed with python and flask.

It includes authentication and authorization with a role based identity and access management.

The role based access management is custom developed.

The api stores and returns data such as staffs, products, sales record, and so on where a staff will have access to send a request to an endpoint based on the role. 

A token is generated for each user which will be used for the authorization when making requests to the API endpoints. The token expires after 12 hours and is being refreshed when the user logs in.

There is also an endpoint to refresh the token.