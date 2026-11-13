import { describe, expect, it } from 'vitest';
import { direction, messages, statusLabel } from './messages';

describe('localization', () => {
  it('provides every message for all locales', () => {
    const keys = Object.keys(messages.en).sort();
    for (const locale of ['ar', 'fa'] as const) {
      expect(Object.keys(messages[locale]).sort()).toEqual(keys);
      expect(Object.values(messages[locale]).every(value => value.trim().length > 0)).toBe(true);
    }
  });
  it('sets RTL direction and translates statuses', () => {
    expect(direction('en')).toBe('ltr');
    expect(direction('ar')).toBe('rtl');
    expect(direction('fa')).toBe('rtl');
    expect(statusLabel('ar', 'pending')).toBe('معلّقة');
    expect(statusLabel('fa', 'cancelled')).toBe('لغوشده');
    expect(statusLabel('en', 'unexpected')).toBe('Unknown');
  });
});
