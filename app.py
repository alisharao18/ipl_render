from flask import Flask, render_template, request, flash
import psycopg2
import os

app = Flask(__name__)
app.secret_key = "supersecretkey"  # needed for flash messages

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.environ.get("DB_HOST"),
            database=os.environ.get("DB_NAME"),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASS"),
            port=os.environ.get("DB_PORT", 5432)
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None

@app.route("/", methods=["GET", "POST"])
def home():
    player = None

    if request.method == "POST":
        name = request.form.get("name")
        new_price = request.form.get("new_price")

        if not name:
            flash("Please enter a player name.", "error")
        else:
            conn = get_db_connection()
            if conn is None:
                flash("Cannot connect to database.", "error")
            else:
                try:
                    cur = conn.cursor()
                    # Fetch player details
                    cur.execute(
                        "SELECT id, name, team, role, country, auction_price FROM players WHERE name=%s",
                        (name,)
                    )
                    player = cur.fetchone()

                    if not player:
                        flash("Player not found!", "error")
                    elif new_price:
                        try:
                            new_price = float(new_price)
                            current_price = float(player[5])
                            if new_price > current_price:
                                # Update auction price
                                cur.execute(
                                    "UPDATE players SET auction_price=%s WHERE id=%s",
                                    (new_price, player[0])
                                )
                                conn.commit()
                                flash(f"Auction price updated to {new_price}", "success")
                                # Fetch updated player
                                cur.execute(
                                    "SELECT id, name, team, role, country, auction_price FROM players WHERE name=%s",
                                    (name,)
                                )
                                player = cur.fetchone()
                            else:
                                flash(f"New price must be higher than current price ({current_price})", "error")
                        except ValueError:
                            flash("Enter a valid number for price", "error")

                    cur.close()
                    conn.close()
                except Exception as e:
                    flash(f"Database query failed: {e}", "error")
                    if conn:
                        conn.close()

    return render_template("app.html", player=player)

if __name__ == "__main__":
    app.run()
