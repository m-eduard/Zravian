Functions from `HomeUI.py` represent the UI options and should be available in
every screen without fulfilling any prior condition. Its up to the user to
provide a suitable environment for the function use. (e.g.:
`press_continue_button()` is to be used after creating a new account or
founding a new village only).<br>
<br>
Functions contained in other modules of `screen` directory: 
- `OverviewVillage.py`;
- `Map.py`;
- `Statistics.py`;
- `Reports.py`;
- `Messages.py`;
- `Profile.py`;<br>

Will each **ensure** its environment using `move_to_*` functions suite and also
return to a *stable state* once the operation is complete - each function will
call `move_to_overview()`.
