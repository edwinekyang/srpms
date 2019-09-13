# Material Design for Angular

This document explains about the basic settings of Material Design for Angular. \
This project uses `Angular Material 8.1.4` 

## Theme

Master theme is declared in `srpms-theme.scss`
### Example
```
$primary: mat-palette($mat-red, 700);
$accent:  mat-palette($mat-grey, 800, 600, 900);
$warn:    mat-palette($mat-orange, A700);
```
`$primary` and other variables are pre-declared to be used in the application.
Changing these values will change the style assigned to the application accordingly.

## High-quality UI components
Angular Material is built with Angular and Typescript. These components serve as an example of how to build Angular UI components that follow best practices.
- Internationalized and accessible so that all users can use them.
- Straightforward APIs that don't confuse developers.
- Behave as expected across a wide variety of use-cases without bugs.
- Behavior is well-tested with both unit and integration tests.
- Customizable within the bounds of the Material Design specification.
- Performance cost is minimized.
- Code is clean and well-documented to serve as an example for Angular developers.

## Browser and screen reader support
Angular Material supports the most recent two versions of all major browsers: Chrome (including Android), Firefox, Safari (including iOS), and IE11 / Edge.

- Windows: NVDA and JAWS with IE11 / FF / Chrome.
- macOS: VoiceOver with Safari / Chrome.
- iOS: VoiceOver with Safari
- Android: Android Accessibility Suite (formerly TalkBack) with Chrome.
- Chrome OS: ChromeVox with Chrome.

## Resources
[Angular Material](https://material.angular.io/) \
[Material Design VS Bootstrap: Which one is better?](https://azmind.com/material-design-vs-bootstrap/)
