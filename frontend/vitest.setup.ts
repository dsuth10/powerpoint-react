import { expect, test, describe, it, beforeEach, afterEach, vi } from 'vitest'

// Make test globals available
global.expect = expect
global.test = test
global.describe = describe
global.it = it
global.beforeEach = beforeEach
global.afterEach = afterEach
global.vi = vi

import '@testing-library/jest-dom' 