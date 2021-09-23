    In order to provide a stable action set within the Framework, all functions
present in screen directory may be called without any prior condition
and should ensure the return to a stable zone (Overview screen) after the
execution is complete.
    In order to do so, the pattern for these functions looks like this:

```
move_to_requiredScreen()
perform_action()
move_to_overview()
```

NOTE: Even if errors are encountered, move_to_overview() must be called
regardless.
