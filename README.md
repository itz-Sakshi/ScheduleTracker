### SCHEDULETRACKER
#### Video Demo: https://youtu.be/O1Vg0tmlpxI

#### APP LINK: http://scheduletracker.onrender.com/

### Description:

Creation of a web application using flask, SQL, HTML and CSS which enables students to keep a track of their everyday tasks, groceries as well as deadlines and ultimately make the best out of their daily 24 hrs :)

All the data in this app has been stored in a SQL database called 'timetable.db' which mainly contains five tables namely, users, study, groceryList, deadlines and others.

First of all, when the app starts, a login page will appear which has been made using the login decorator function in the 'app.py', and 'login.html'. In this page, the user can login to their personal account if they have already registered. However, if it is a new user, a register button is available. Click on the register button and the register page will be displayed. The register page has been made using the register decorator function in the 'app.py', and 'register.html'. Fill in the username and password and then, confirm password and then, click on register.

Subsequently, the user gets registered and his username and password gets added in the users table. The user is directed to the login page and he can directly login now whenever he wants to open the app. After logging in, the user is directed to the index page. There, the user can see the heading "Today's To do list" under which all his tasks to be done for today will appear after he assigns them. Similarly, below this, all the deadlines for the next 10 days will appear.

If the user clicks on the study link, he will be sent to the study page. There, he can see the study schedule table where he can add a new study task. He needs to first type the task and then select the date and click on the 'add new task' button. All this information gets stored in the study table. The deadlines and the others link also function in the same way but their information gets stored in their respective tables.

Other than these, there is also a grocery link which directs the user to the grocery page, where the user can make a list of his grocery items. The information related to groceries is stored in the grocery table. Lastly, there is a pending link. By clicking on it, the user is sent to the pending page where all the pending work will be displayed.

All the pages have a 'delete' and a 'done' button which can be used to delete a particular task or item.
