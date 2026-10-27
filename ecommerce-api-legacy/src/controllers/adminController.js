class AdminController {
    constructor({ reportService }) {
        this.reportService = reportService;
        this.financialReport = this.financialReport.bind(this);
    }

    async financialReport(req, res) {
        res.json(await this.reportService.financialReport());
    }
}

module.exports = AdminController;
