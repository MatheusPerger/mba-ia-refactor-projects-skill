class UserController {
    constructor({ userService }) {
        this.userService = userService;
        this.remove = this.remove.bind(this);
    }

    async remove(req, res) {
        await this.userService.remove(req.params.id);
        res.send('Usuário deletado.');
    }
}

module.exports = UserController;
