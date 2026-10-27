const { AppError } = require('../errors');

const isNonEmptyString = (value) => typeof value === 'string' && value.length > 0;

class CheckoutController {
    constructor({ checkoutService }) {
        this.checkoutService = checkoutService;
        this.checkout = this.checkout.bind(this);
    }

    async checkout(req, res) {
        const { usr: name, eml: email, pwd: password, c_id: courseId, card } = req.body || {};

        if (!isNonEmptyString(name) || !isNonEmptyString(email) || !isNonEmptyString(card) || !courseId) {
            throw new AppError(400, 'Bad Request');
        }
        if (password !== undefined && password !== null && typeof password !== 'string') {
            throw new AppError(400, 'Bad Request');
        }

        const enrollmentId = await this.checkoutService.checkout({ name, email, password, courseId, card });
        res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollmentId });
    }
}

module.exports = CheckoutController;
