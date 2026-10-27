const { AppError } = require('../errors');
const { PAYMENT_STATUS, APPROVED_CARD_PREFIX } = require('../config/constants');

class CheckoutService {
    constructor({ userModel, courseModel, enrollmentModel, passwordService, logger }) {
        this.userModel = userModel;
        this.courseModel = courseModel;
        this.enrollmentModel = enrollmentModel;
        this.passwordService = passwordService;
        this.logger = logger;
    }

    async checkout({ name, email, password, courseId, card }) {
        const course = await this.courseModel.findActiveById(courseId);
        if (!course) throw new AppError(404, 'Curso não encontrado');

        const userId = await this.findOrCreateUser({ name, email, password });

        const paymentStatus = this.processPayment(card);
        if (paymentStatus === PAYMENT_STATUS.DENIED) throw new AppError(400, 'Pagamento recusado');

        const enrollmentId = await this.enrollmentModel.enrollWithPayment({ userId, course, paymentStatus });
        this.logger.info(`Checkout curso ${course.id} por usuário ${userId}`);
        return enrollmentId;
    }

    async findOrCreateUser({ name, email, password }) {
        const user = await this.userModel.findByEmail(email);
        if (user) return user.id;

        if (!password) throw new AppError(400, 'Bad Request');
        const passwordHash = await this.passwordService.hash(password);
        return this.userModel.create({ name, email, passwordHash });
    }

    // Simulação do gateway: cartões iniciados em "4" são aprovados.
    processPayment(card) {
        return card.startsWith(APPROVED_CARD_PREFIX) ? PAYMENT_STATUS.PAID : PAYMENT_STATUS.DENIED;
    }
}

module.exports = CheckoutService;
