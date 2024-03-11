# Tennis
The Tennis Court Booking System is a web-based application designed to
facilitate the management of bookings for a tennis court. It allows users to schedule court
reservations, receive notifications about their bookings, and enables administrators to
oversee the booking process. Additionally, the system notifies designated workers to clean
the court after each game session.

## Requirements
- Docker
- Docker-Compose
- A working internet connection

## Installation
1. Clone the repository
2. In the repo, create a `.env` folder
3. In the `.env` folder. Create the `api.env` file.
   ```env
   SECRET_KEY=<secret_key>
   DEBUG=True
   ALLOWED_HOSTS=*
   REDIS_HOST=redis
   POSTGRES_HOST=db
   ```
5. In the `.env` folder. Create the `db.env` file.
   ```env
   POSTGRES_USER=<db username>
   POSTGRES_PASSWORD=<db password>
   POSTGRES_DB=<db name>
   ```
6. Navigate to the repo folder and start the containers in 
   ```bash
   docker-compose up
   ```
8. Create a superuser to access the admin panel. Include an email address for notifications
   ```
   docker exec -it tennis_api python manage.py createsuperuser
   ```
9. Access the API via `http://localhost`
10. Aceess the admin panel via `http://localhost/admin`. Log in with the superuser credentials


## Documentation
The documentation for the REST API can be accessed by serving the `index.html` located in the `docs` folder, for example, with
the Live Server extension on VS Code

## Websocket
The websocket can accessed from `ws://localhost/ws/bookings?token=<JWT>`. A valid JWT may be obtained from the REST API. 
##### Subscribe to bookings feed
This message is used to subscribe to the bookings feed for a specific court to update the available slots
```json
{
  "type": "sub",
  "court_id": <court_id>
}
```
##### Unsubscribe to bookings feed
This message is used to unsubscribe from a booking feed
```json
{
  "type": "unsub",
  "court_id": <court_id>
}
```
##### Place booking
This message is used to book a court from a specified time for a specified duration(hours)
```json
{
  "type": "book",
  "court_id": <court_id>,
  "start_time": YYYY-mm-dd HH:SS,
  "duration" : int
}
```
A successful booking generates a broadcast message with the following json format and sends notifications to admins and users. Notifications are displayed in the console
```json
{
  "booked" : {
      "start_time": YYYY-mm-dd HH:SS,
      "end_time" : YYYY-mm-dd HH:SS
  }
}
```
##### Cancel booking
This message is used to cancel a booking
```json
{
  "type": "cancel",
  "booking_id" : <booking_id>
}
```
A successful cancellation generates a broadcast message with the following json format and sends notifications to admins and users. Notifications are displayed in the console
```json
{
  "cancelled" : {
      "start_time": YYYY-mm-dd HH:SS,
      "end_time" : YYYY-mm-dd HH:SS
  }
}
```




