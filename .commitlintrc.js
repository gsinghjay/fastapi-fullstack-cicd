module.exports = {
    extends: ['@commitlint/config-conventional'],
    rules: {
        'type-enum': [2, 'always', [
            'feat',
            'fix',
            'docs',
            'style',
            'refactor',
            'perf',
            'test',
            'build',
            'ci',
            'chore',
            'revert'
        ]],
        'scope-empty': [2, 'never'],
        'subject-case': [2, 'always', 'sentence-case'],
        'subject-empty': [2, 'never'],
        'subject-full-stop': [2, 'never', '.'],
        'header-max-length': [2, 'always', 72],
    }
};
