import unittest

from string_interning_pool_tools import InternedString, StringPool


class InternedStringTests(unittest.TestCase):
    def test_value_property(self):
        handle = InternedString("alpha")
        self.assertEqual(handle.value, "alpha")
        self.assertEqual(str(handle), "alpha")

    def test_equality_with_str_and_handle(self):
        handle = InternedString("alpha")
        self.assertEqual(handle, "alpha")
        self.assertEqual(handle, InternedString("alpha"))
        self.assertNotEqual(handle, "beta")

    def test_hash_matches_str(self):
        handle = InternedString("alpha")
        self.assertEqual(hash(handle), hash("alpha"))
        self.assertEqual({handle: 1}, {"alpha": 1})

    def test_rejects_non_str(self):
        with self.assertRaises(TypeError):
            InternedString(123)


class StringPoolTests(unittest.TestCase):
    def test_intern_returns_same_object_for_repeated_value(self):
        pool = StringPool()
        first = pool.intern("hello")
        second = pool.intern("hello")
        self.assertIs(first, second)

    def test_intern_distinguishes_different_values(self):
        pool = StringPool()
        self.assertIsNot(pool.intern("a"), pool.intern("b"))
        self.assertEqual(len(pool), 2)

    def test_intern_rejects_non_str(self):
        pool = StringPool()
        with self.assertRaises(TypeError):
            pool.intern(42)

    def test_interned_wraps_canonical_value(self):
        pool = StringPool()
        handle = pool.interned("beta")
        self.assertIsInstance(handle, InternedString)
        self.assertIs(handle.value, pool.intern("beta"))

    def test_intern_all_preserves_order(self):
        pool = StringPool()
        result = pool.intern_all(["x", "y", "x"])
        self.assertEqual(result, ["x", "y", "x"])
        self.assertIs(result[0], result[2])
        self.assertEqual(len(pool), 2)

    def test_get_does_not_insert(self):
        pool = StringPool()
        pool.intern("present")
        self.assertEqual(pool.get("present"), "present")
        self.assertIsNone(pool.get("absent"))
        self.assertEqual(len(pool), 1)

    def test_contains_accepts_only_str(self):
        pool = StringPool()
        pool.intern("yes")
        self.assertTrue("yes" in pool)
        self.assertFalse("no" in pool)
        self.assertFalse(5 in pool)

    def test_initial_values_are_interned(self):
        pool = StringPool(["one", "two", "one"])
        self.assertEqual(len(pool), 2)
        self.assertIs(pool.intern("one"), pool.get("one"))

    def test_values_returns_snapshot_tuple(self):
        pool = StringPool(["a", "b"])
        snapshot = pool.values()
        self.assertIsInstance(snapshot, tuple)
        self.assertEqual(sorted(snapshot), ["a", "b"])
        pool.intern("c")
        self.assertEqual(len(snapshot), 2)

    def test_clear_empties_pool_but_keeps_handles(self):
        pool = StringPool()
        handle = pool.interned("keep")
        pool.clear()
        self.assertEqual(len(pool), 0)
        self.assertEqual(handle.value, "keep")

    def test_whitespace_and_case_are_not_normalised(self):
        pool = StringPool()
        self.assertIsNot(pool.intern("a"), pool.intern("a "))
        self.assertIsNot(pool.intern("a"), pool.intern("A"))
        self.assertEqual(len(pool), 3)

    def test_iter_yields_canonical_strings(self):
        pool = StringPool(["p", "q"])
        self.assertEqual(sorted(pool), ["p", "q"])


if __name__ == "__main__":
    unittest.main()
