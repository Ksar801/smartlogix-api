from flask import Flask, request, jsonify, render_template
import psycopg2
import os

# Configurar Flask para que busque los templates en la misma carpeta que app.py
app = Flask(__name__, template_folder=".")

# ---- Configuración de la BD ----
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

def get_connection():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

# ---- Rutas API ----

@app.route("/students", methods=["POST"])
def create_student():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO students (nombre, correo) VALUES (%s, %s) RETURNING id;",
        (data["nombre"], data["correo"])
    )
    student_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": student_id}), 201

@app.route("/courses", methods=["POST"])
def create_course():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO courses (titulo, descripcion) VALUES (%s, %s) RETURNING id;",
        (data["titulo"], data.get("descripcion", None))
    )
    course_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": course_id}), 201

@app.route("/enrollments", methods=["POST"])
def enroll_student():
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO enrollments (student_id, course_id, puntaje, estado)
           VALUES (%s, %s, 100, 'Activo') RETURNING id;""",
        (data["student_id"], data["course_id"])
    )
    enrollment_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"id": enrollment_id}), 201

@app.route("/enrollments/<int:enroll_id>", methods=["PUT"])
def update_enrollment(enroll_id):
    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE enrollments SET estado = %s WHERE id = %s;",
        (data["estado"], enroll_id)
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Estado actualizado"}), 200

@app.route("/students/<int:student_id>/enrollments", methods=["GET"])
def get_student_enrollments(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """SELECT c.titulo, e.estado, e.puntaje, e.fecha_matricula
           FROM enrollments e
           JOIN courses c ON e.course_id = c.id
           WHERE e.student_id = %s;""",
        (student_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    result = [
        {"curso": r[0], "estado": r[1], "puntaje": r[2], "fecha": r[3]} for r in rows
    ]
    return jsonify(result), 200

# ---- Página HTML para registro manual ----
@app.route("/form")
def form():
    return render_template("llenar_datos.html")  # buscará el HTML en la misma carpeta

@app.route("/registrar", methods=["POST"])
def registrar():
    nombre = request.form["nombre"]
    correo = request.form["correo"]
    titulo = request.form["titulo"]
    descripcion = request.form["descripcion"]

    conn = get_connection()
    cur = conn.cursor()

    # Insertar estudiante
    cur.execute(
        "INSERT INTO students (nombre, correo) VALUES (%s, %s) RETURNING id;",
        (nombre, correo)
    )
    student_id = cur.fetchone()[0]

    # Insertar curso
    cur.execute(
        "INSERT INTO courses (titulo, descripcion) VALUES (%s, %s) RETURNING id;",
        (titulo, descripcion)
    )
    course_id = cur.fetchone()[0]

    # Insertar matrícula
    cur.execute(
        "INSERT INTO enrollments (student_id, course_id, puntaje, estado) VALUES (%s, %s, 100, 'Activo');",
        (student_id, course_id)
    )

    conn.commit()
    cur.close()
    conn.close()

    return f"Estudiante y curso registrados correctamente. Estudiante ID: {student_id}, Curso ID: {course_id}"

# ---- Ruta home ----
@app.route("/")
def home():
    return jsonify({"mensaje": "La API de SmartLogix está funcionando ✅"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
