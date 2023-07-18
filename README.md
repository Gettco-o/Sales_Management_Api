The sales management api was developed with python and flask.

It includes authentication and authorization with a role based identity and access management.

The role based access management is custom developed, no third party sites (e.g auth0..) was used as SaaS.

The api stores and returns data such as staffs, products, sales record, and so on where a staff will have access to send a request to an endpoint based on the role. 

A token is generated for each user which will be used for the authorization when making requests to the API endpoints.