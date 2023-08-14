functionality of each function in the code 

  

1. is_ip_blocked 

This function checks if the given ip_address is blocked by querying the BlockedIP model using Django's Object-Relational Mapping (ORM) system. It returns True if there is a record in the BlockedIP model with the given IP address, otherwise False 

  

2. is_ip_permently_blocked 

 This function checks if the given ip_address is permanently blocked by querying the PermanentBlockedIP model with the is_permanently_blocked attribute set to True.It returns True if there is a record in the PermanentBlockedIP model with the given IP address and the is_permanently_blocked field set to True, otherwise False 

  

3. block_ip 

 This function blocks the given ip_address by creating a record in the BlockedIP model if it doesn't already exist. If the IP address is already blocked, it updates the corresponding BlockedIP record to reset the failed login attempts count to 0.It also creates a BlockedIO object associated with the blocked IP address, which stores information about the blocking event (e.g., manual blocking, login attempt blocking).The io_type parameter specifies the type of blocking (defaults to manual).The duration_minutes parameter determines the duration for which the IP address will be blocked (defaults to 10 minutes) 

  

4. unblock_ip 

This function unblocks the given ip_address by deleting the corresponding BlockedIP record. It checks if a record exists for the IP address, and if so, it deletes the record 

  

5. get_blocked_ips 

This function retrieves a list of all blocked IP addresses from the BlockedIP model using the values_list method.It returns a Python list containing the blocked IP addresses. 

  

6. block_ip_manually 

This function manually blocks a list of IP addresses specified in the ip_addresses parameter.It iterates through each IP address and blocks it using the block_ip function.If an IP address is already in the blocked_request_tracker and it is marked as blocked, it skips the block request for that IP address. 

  

7. handle_failed_login 

This function handles failed login attempts for a specific IP address and user. It first creates a cache key based on the IP address to store the login attempts count in the cache. It retrieves the current login attempts count from the cache. If the cache key doesn't exist, it defaults to 0.If there have been five consecutive failed login attempts for the same IP address, it stores the IP address in the FailedLoginAttempt model, blocks the IP address temporarily for 10 minutes using the block_ip function, and returns a 403 Forbidden response with a message. If there have been less than five failed login attempts, it updates the count in the FailedLoginAttempt model or creates a new record for the IP address if it doesn't exist. The cache is updated with the new login attempts count and set to expire after 10 minutes. If there have been three or more failed login attempts, it sets the captcha_url to show a CAPTCHA to prevent automated login attempts. Finally, it constructs a warning message indicating the number of remaining attempts (up to 5 attempts) for the user to log in successfully and returns a 403 Forbidden response with the warning message


workflow

The middleware first checks if the IP address is permanently blocked by calling the is_ip_permently_blocked method. If it is permanently blocked, a 403 Forbidden response is returned. 

If the IP address is not permanently blocked, the middleware then checks if the IP address is temporarily blocked by calling the is_ip_blocked method. If it is temporarily blocked, a 403 Forbidden response is returned. 

If the IP address is not blocked, the request is passed to the next middleware or view function in the chain. 

If the response status code is 401 (Unauthorized), indicating a failed login attempt, the middleware calls the handle_failed_login method to handle the failed login attempts. Depending on the number of attempts, either a temporary block is applied and a 403 Forbidden response is returned, or a warning message is returned with the remaining attempts count. 
