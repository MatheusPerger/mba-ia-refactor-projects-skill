const express = require('express');
const config = require('./config');
const logger = require('./logger');
const Database = require('./database');
const { createSchema, seed } = require('./database/schema');
const passwordService = require('./services/passwordService');
const UserModel = require('./models/userModel');
const CourseModel = require('./models/courseModel');
const EnrollmentModel = require('./models/enrollmentModel');
const CheckoutService = require('./services/checkoutService');
const ReportService = require('./services/reportService');
const UserService = require('./services/userService');
const CheckoutController = require('./controllers/checkoutController');
const AdminController = require('./controllers/adminController');
const UserController = require('./controllers/userController');
const buildRoutes = require('./routes');
const errorHandler = require('./middlewares/errorHandler');

async function main() {
    const db = new Database(config.databasePath);
    await createSchema(db);
    await seed(db, passwordService);

    const userModel = new UserModel(db);
    const courseModel = new CourseModel(db);
    const enrollmentModel = new EnrollmentModel(db);

    const checkoutService = new CheckoutService({ userModel, courseModel, enrollmentModel, passwordService, logger });
    const reportService = new ReportService({ enrollmentModel });
    const userService = new UserService({ userModel });

    const app = express();
    app.use(express.json());
    app.use(buildRoutes({
        checkoutController: new CheckoutController({ checkoutService }),
        adminController: new AdminController({ reportService }),
        userController: new UserController({ userService }),
        adminToken: config.adminToken
    }));
    app.use(errorHandler);

    app.listen(config.port, () => logger.info(`Frankenstein LMS rodando na porta ${config.port}...`));
}

main().catch((err) => {
    logger.error(err.stack || String(err));
    process.exit(1);
});
