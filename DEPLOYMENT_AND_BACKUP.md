# Deployment Instructions for Odoo Catering Module

## Prerequisites

- Docker and Docker Compose installed
- PostgreSQL database (can be run as a container)
- Required environment variables set (see .env.example if available)

## Steps

1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd odoo-catering
   ```

````
2. **Configure Environment:**
   - Copy and edit `odoo.conf.example` to `odoo.conf` as needed.
   - Update any environment variables in `.env` if present.
3. **Build and Start Containers:**
   ```sh
docker-compose up --build -d
````

4. **Initialize Database (if first run):**
   - The Odoo container will automatically initialize the database if it does not exist.
5. **Access the Application:**
   - Open your browser and go to `http://localhost:8069` (or the port specified in your configuration).

## Additional Notes

- To stop the application: `docker-compose down`
- To view logs: `docker-compose logs -f`
- For custom modules, place them in the appropriate `addons` directory and update `odoo.conf`.

---

# Backup and Restore Instructions

## Database Backup

1. **Using Docker Compose:**
   ```sh
   docker exec -t <db_container_name> pg_dumpall -c -U <db_user> > db_backup.sql
   ```

````
   - Replace `<db_container_name>` and `<db_user>` with your actual container and user names.

2. **Manual PostgreSQL Backup:**
   ```sh
pg_dump -U <db_user> <db_name> > db_backup.sql
````

## File Storage Backup

- Back up the `filestore` directory, usually found in `~/.local/share/Odoo/filestore` or as configured in your Odoo settings.

## Restore

1. **Database Restore:**
   ```sh
   docker exec -i <db_container_name> psql -U <db_user> <db_name> < db_backup.sql
   ```

```
2. **File Storage Restore:**
   - Replace the `filestore` directory with your backup copy.

## Recommendations
- Schedule regular backups of both the database and filestore.
- Test your restore process periodically.
```
