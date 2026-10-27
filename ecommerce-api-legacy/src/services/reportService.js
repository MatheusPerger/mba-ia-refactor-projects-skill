const { PAYMENT_STATUS } = require('../config/constants');

class ReportService {
    constructor({ enrollmentModel }) {
        this.enrollmentModel = enrollmentModel;
    }

    async financialReport() {
        const rows = await this.enrollmentModel.listReportRows();
        const coursesById = new Map();

        for (const row of rows) {
            if (!coursesById.has(row.course_id)) {
                coursesById.set(row.course_id, { course: row.course_title, revenue: 0, students: [] });
            }
            if (row.enrollment_id === null) continue;

            const entry = coursesById.get(row.course_id);
            if (row.payment_status === PAYMENT_STATUS.PAID) entry.revenue += row.payment_amount;
            entry.students.push({
                student: row.user_name || 'Unknown',
                paid: row.payment_amount || 0
            });
        }

        return [...coursesById.values()];
    }
}

module.exports = ReportService;
