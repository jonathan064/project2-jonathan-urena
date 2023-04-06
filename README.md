projecttest.fly.dev

First I had to set up all of the database stuff by installing flask sqlalchemy
Then we need to create the table with all of our desired fields.
Afterwards its only a matter of figuring out how to pass the differenet information to and from the database in order to render it properly.

The main issue I encountered over the course of this project is in setting uo my sql tables correctly. I accidentally set the wrong attributes to unique which ended up causing several issues when adding multiple comments from the same user. Similarly, I had to find a workaround when registering users because my post request would always retrieve something called 'favicon.ico'(not sure what it was) so I had to check if that was being passed in order to avoid adding it to the db and messing up the primary key for users. Another issue I had was in passing the correct movie_id to the db. Originally I was passing it the id through the get_movie_by_id() function but for some reason it would only work sometimes. It wasn't until after I used the readonly input that it worked fine.

Setting up the db was fairly easy. However, adding the correct values and passing everything needed was a bit more difficult than I anticipated. However, one of the things that was really easy was setting up the login and registration functions. I assumed that it would be more difficult but the flask_login extension does a lot of the work. Displaying information from the db was also surprisingly easy. I feel much more confident in using db and jinja now after this project.