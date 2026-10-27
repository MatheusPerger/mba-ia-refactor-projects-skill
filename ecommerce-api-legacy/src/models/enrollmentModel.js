class EnrollmentModel {
    constructor(db) {
        this.db = db;
    }

    // Enrollment + payment + audit log em uma única transação.
    enrollWithPayment({ userId, course, paymentStatus }) {
        return this.db.transaction(async () => {
            const enrollment = await this.db.run(
                'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
                [userId, course.id]
            );
            await this.db.run(
                'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
                [enrollment.lastID, course.price, paymentStatus]
            );
            await this.db.run(
                "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
                [`Checkout curso ${course.id} por ${userId}`]
            );
            return enrollment.lastID;
        });
    }

    // Uma única query traz cursos, alunos e pagamentos (evita N+1).
    listReportRows() {
        return this.db.all(`
            SELECT c.id AS course_id,
                   c.title AS course_title,
                   e.id AS enrollment_id,
                   u.name AS user_name,
                   p.amount AS payment_amount,
                   p.status AS payment_status
            FROM courses c
            LEFT JOIN enrollments e ON e.course_id = c.id
            LEFT JOIN users u ON u.id = e.user_id
            LEFT JOIN payments p ON p.enrollment_id = e.id
            ORDER BY c.id, e.id
        `);
    }
}

module.exports = EnrollmentModel;
