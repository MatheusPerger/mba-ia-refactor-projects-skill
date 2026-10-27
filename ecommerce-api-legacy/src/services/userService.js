class UserService {
    constructor({ userModel }) {
        this.userModel = userModel;
    }

    remove(id) {
        return this.userModel.deleteWithDependents(id);
    }
}

module.exports = UserService;
