import os
import yaml
import utils

def main():
    try:
        print("Fetching database credentials from AWS Secrets Manager...")
        sm = utils.SecretCache(region="us-east-1")
        db_creds = sm.get("MySQL_local")
        
        compose = {
            "version": "3.8",
            "services": {
                "db": {
                    "image": "mysql:8.4",
                    "container_name": "mailer_db",
                    "restart": "unless-stopped",
                    "environment": {
                        "MYSQL_ROOT_PASSWORD": "root", 
                        "MYSQL_DATABASE": db_creds.get("database"),
                        "MYSQL_USER": db_creds.get("user"),
                        "MYSQL_PASSWORD": db_creds.get("password")
                    },
                    "ports": [
                        "3306:3306" 
                    ],
                    "volumes": [
                        "/home/vsarthak/all_db_backup_22march2026.sql:/docker-entrypoint-initdb.d/init.sql",
                        "mailer_db_data:/var/lib/mysql"
                    ]
                }
            },
            "volumes": {
                "mailer_db_data": None
            }
        }
        
        with open("docker-compose.yml", "w") as f:
            yaml.dump(compose, f, sort_keys=False)
            
        print("Successfully generated docker-compose.yml with your AWS credentials!")
        print("You can now connect your container using:")
        print(" > docker compose up -d")
        
    except Exception as e:
        print(f"Error fetching AWS credentials: {e}")

if __name__ == "__main__":
    main()
