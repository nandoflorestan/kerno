========
Concepts
========

Kerno wishes to support:

- the storage of a log of commands (for auditing, telling us who did what);
- live updating of a UI - for example, through WebSockets;
- an undo feature.

To this end, Kerno shall use the following concepts:

**User**: The user (or system component) that performs an Operation.

**Where**: This is the context of an Operation -- which object(s) will be affected --, such as what division, what round etc.

**State**: Can be stored as a pickle. Preferably as JSON.

**Manual**: A list of available Operations that the controller (the UI)
can call, with an explanation of their parameters.

**Query**: A non-destructive Operation as seen from the controller (the UI).
  - Validates the Where (e. g. does this round belong to this division?)
  - Verifies the User's authorization.
  - Returns data.

**Action**: A step in an Operation.

**Operation**: A named series of Actions, as seen from the controller (the UI).
Some of the Actions would be:
  - Validate the Where (e. g. does this round belong to this division?)
  - Verify the User's authorization.
  - Validate incoming data (usually).
  - Create a State for the Undo -- i. e. the current state.
  - Create a State for the Do -- i. e. the future state.
  - Instantiate a Command with the Where and the 2 States.
  - In a transaction:
    - Execute the Do function of the Command.
    - Store the Command in the History.

**History**: Enables logging and undo. A stack of Commands with all their data. May have multiple storage backends. Might save space by making an Undo state point to a previously stored state.

**Command**: Enables undo. Stored in History. Contains the date, the User, the Do function, the Where, the Undo function, the Do and Undo States, and a brief description. Sometimes both functions will be the same (e. g. just a setter), but other times they will need to be different functions.

In the future, we might also have:

**Order**: A composite Command, or a named sequence of Commands. The History needs to support storage of Commands and Orders. Not sure how an Action instantiates an Order.

**Impact**: We can allow the execution of Undos out of order, as long as we know their Impact. For instance, the Command "Rename a division" impacts other commands of the same name, but does not impact an "Add round to division" command.

**Fact**: In the same timeline of the History we may wish to store events that have no Impact at all, for auditing. For instance, "On 2016-11-20 the user Nando logged in", or "Backup ran", or "Round started".
