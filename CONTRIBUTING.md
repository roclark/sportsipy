# Contributing
`Sportsipy` is an open-source project created for the community where
contributions are encouraged. I ask that anyone who wishes to contribute to
please read and follow the guidelines listed below. As the project grows and
changes, so too will this document. If any items are no longer relevant or need
to be adjusted, feel free to suggest changes in a Pull Request or Issue.

## Code of Conduct
By using this repository, you are expected to abide by the rules listed in the
[Code of Conduct](CODE_OF_CONDUCT.md). Any behavior that is not in-line with the
Code of Conduct should be reported to the project maintainers.

## How Can I Contribute?
Contributions from the community make open-source projects awesome and
developers, data scientists, hobbyists, and more are encouraged to contribute to
`sportsipy`. The following are some examples on how to contribute to this
project.

### Reporting bugs
The biggest way to contribute to this project is by reporting any and all bugs
that are encountered while using the tool. The best way to report a bug is to
file an issue on GitHub with as much detailed information as possible on what's
not working, what the expected outcome is, and how the issue can be reproduced.
From there, if the issue can be duplicated, one of the community members,
including but not limited to the maintainers, will follow up to address the
issue and create an update if deemed necessary.

### Suggesting new features
Another way to improve the project is by suggesting new features. When
suggesting a new feature, a GitHub issue should be opened with information on
what the feature is, what makes it valuable, and examples or suggestions on how
to implement it. In general, a new feature should be filed prior to creating a
Pull Request so the community can discuss the proper way to incoporate the idea,
or if it should be tweaked at all.

### Updating documentation and tests
One of the easiest ways to become a contributor to this project is by updating
documenation and enhancing or expanding tests. Documenation updates include
expanding the current documentation, adding more examples of how to use the
package, and spelling and/or grammatical fixes.

### Creating a pull request
Pull Requests should have a common theme or idea for the contents of an update.
If updates span several different areas, they should be split into separate Pull
Requests for each theme.

As with the git commit message styling guidelines down below, Pull Requests
should contain information detailing the need for the update, why the changes
were made the way they were committed, and if it resolves any outstanding
issues.

## Styling
To ensure the highest level of quality not only with the code but also with the
overall structure of the project, several styling guidelines should be followed.

### Git commit message
The git commit message is a crucial part of any code update and should follow
certain guidelines to describe what the commit is for, why it the changes are
being made, and who wrote the commit. A great resource on writing a strong
commit message can be found [here](https://chris.beams.io/posts/git-commit/).
The seven rules should be followed unless a compelling circumstance arises.
These rules are as follows (taken from the linked page):
  1. Separate subject from body with a blank line
  2. Limit the subject line to 50 characters
  3. Capitalize the subject line
  4. Do not end the subject line with a period
  5. Use the imperative mood in the subject line
  6. Wrap the body at 72 characters
  7. Use the body to explain _what_ and _why_ vs. _how_

In addition to these rules, a few others should be considered. First, all commit
bodys should end with `Signed-Off-By: First Last <email@domain.com>`. The
following example shows how the signature should be applied:

```
Fix failing NCAAB functional test

The NCAAB functional test fails whenever a team has an ampersand in
their name, so special parsing should be used to transform this
character to something sports-reference can utilize.

Signed-Off-By: John Doe <john@gmail.com>
```

Lastly, commits should be separated only when necessary. For example, instead of
having two commits where the second fixes an issue created by the first, rebase
the two commits to a single commit. Take the following visual example:

```
$ git log --oneline

e15d67b Add a Code of Conduct
1479ac0 Fix typo in Code of Conduct
```

Since the first commit created a file and the second commit fixed an issue
created from that commit, they should be combined into a single commit.

On the other hand, commits should be specific and the update should have a
limited scope. As an example, a commit that creates a Code of Conduct as well as
fixes an issue in a unit test should be split into at least two different
commits; one for creating the Code of Conduct, and one for fixing the unit test
issue.

### Python style
In general, all Python code should follow the Python Enhanced Proposals (PEPs).
The continuous integration tool used to qualify the project runs `pycodestyle`
which attempts to verify the code against the PEP rules and warn if any
violations have been made. If a particular PEP rule is being violated but is
deemed to be necessary, exceptions can be made on a case-by-case basis.
Otherwise, all code must pass `pycodestyle` prior to being merged with the
upstream code.

## General Practice
Outside of the above guidelines, several general best practices should be
followed for all code contributions.

### Documentation
Whenever new features are included, the API changes, or the functionality of
existing classes or modules changes, documenation should be modified
appropriately to reflect those updates. This includes, but is not limited to,
adding heredocs to classes, functions, methods, and properties, writing
documenation in the docs section to explain the usage and purpose of new
classes, and update existing documentation when classes have been modified in a
way that they no longer follow the description in the existing documenation.

### Unit/Functional tests
Whenever new code is added to the repository, either functional tests or unit
tests should be included to ensure the new code is fully tested over different
scenarios. Examples can be found in the tests directory.

In addition to adding tests for new code, all existing tests should pass unless
there is an issue with one of the actual tests. In that case, the maintainers
should be notified of this issue to ensure a resolution is found.
