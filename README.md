# 🌐 PruneURL

**PruneURL** is a secure, feature-rich URL shortener with **analytics and admin controls**—easy to self-host for **teams and businesses**.

Backend built using **[Python](https://python.org)**, **[Flask](https://flask.palletsprojects.com/en/stable/)** and **[PostgreSQL](https://www.postgresql.org/)**. Caching for rate limiting performed by **[Redis](https://redis.io/)**. Front-end developed in HTML, CSS and TypeScript (compiled to JavaScript).

🗝️ This app is perfect for businesses, teams, or individuals who want full control over their short links and analytics—no third-party cloud required.

## 🌠 Features

- 👤 User account system with **flexible limits** to prevent abuse
- ⚠️ Warning upon clicking links to **prevent open redirects**
- 🎭 JWT-powered **Role-Based Access Control (RBAC)** with an admin panel
- 📊 See which links/users are attracting traffic from search/filter features in the **admin panel**
- 🛑 Sensible **rate limits** on sensitive endpoints
- 🔒 Secure **hashing + salting** of passwords using **[bcrypt](https://pypi.org/project/bcrypt/)**
- 📱 **Elegant and responsive design** for all screen sizes
- 🌱 Easy to **self-host** in just a **few steps** (described below)

## 🧊 Dependencies

1. Install [Python](https://python.org) on your system.
2. Install [PostgreSQL](https://www.postgresql.org/) on your system and start the server.
3. Install [Redis](https://redis.io/downloads/) **(optional but recommended, read below)**

**Note:** If you don't install Redis, the rate limiter will fallback to in-memory storage instead. The app will still work, but this is not recommended if you have plan on having many users.

## 🚀 Building from Source

1. First, clone the repository:

```bash
git clone https://github.com/pranavcl/prune-url
```

2. Enter the cloned directory and run `pip install -r requirements.txt`:

```bash
cd prune-url
pip install -r requirements.txt
```

3. Create a `.env` file in the **root directory (./prune-url)** and define the values of **`DB_PASS`** and **`SECRET_KEY`** (mandatory) like so:


```
DB_PASS=a
SECRET_KEY=<your-secret-key>
```

4. **(Optional)** You can also set other environment variables:

- **ADMIN_PASS:** Password for the admin account (a@a.com), default value: `a`. It is highly recommended that you change this.
- **BASE_URL:** Used to construct shortened URLs, default value: `http://localhost:2000`
- **PORT:** Port on which the app runs, default value: 2000
- **REDIS:** Points to redis, default value: `redis://localhost:11211`
- **DB_HOST:** Hostname of the Postgres server, default value: `localhost`
- **DB_PORT:** Port on which Postgres is running, default value: `5432`
- **DB_NAME:** Name of the database where all the relations will be stored, default value: `pruneurl`
- **DB_USER:** Username for Postgres, default value: `postgres`

5. **(Optional)** Additionally, if you want forgot and reset password functionality to work, you MUST also define the environment variables **`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`** and **`MAIL_PASSWORD`** like so:

```
MAIL_SERVER=smtp.yourdomain.com
MAIL_PORT=465 (or whatever the SSL port is on your mailserver)
MAIL_USERNAME=example@yourdomain.com
MAIL_PASSWORD=(your email account's password)
```

6. Make sure that Postgres and Redis are running. Then, run the app using `python`:

```
python run.py
```

**All done!** 🎉

## License

Published under the [PruneURL license](https://github.com/pranavcl/prune-url/blob/main/LICENSE.md)