from .action import Action


class LoggerAction(Action):
    """Action that logs the operation details onto a storage backend.

    This action can be used in any operation. It is probably preferable to
    place this action after all the other actions in the operation.

    The application must register a utility called "logger repository"
    offering a ``log`` method
    """

    def __call__(self):
        peto = self.peto
        storage = peto.kerno.get_utility('logger repository')
        storage.log(
            when=peto.when,
            user=peto.user.id if hasattr(peto.user, 'id') else str(peto.user),
            operation=peto.operation,
            payload=peto.clean if peto.clean else peto.dirty,
        )
