{
  'target_defaults': {
    'default_configuration': 'Debug',
    'configurations': {
      'Debug': {
        'define': [
          'DEBUG'
        ],
        'cflags': [
          '-g',
          '-O0',
        ],
      },
      'Release': {
        'cflags': [
          '-O3',
        ],
      },
    }
  },
}
