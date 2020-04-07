/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on December 29, 2013
 * sgjava@gmail.com
 */
package com.codeferm.opencv;

/**
 * A "four character code" (4CC), as used in AVI files.
 *
 * This class wraps a 32-bit value to be used as a 4CC inside an AVI file, so
 * that it is guaranteed to be valid, and it incurs no overhead if used
 * repeatedly.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
final class FourCC {
    /**
     * Integer FourCC value.
     */
    private final transient int value;

    /**
     * Convert FourCC String value to int.
     *
     * @param fourcc
     *            FourCC String.
     */
    FourCC(final String fourcc) {
        if (fourcc == null) {
            throw new IllegalArgumentException("FourCC cannot be null");
        }
        if (fourcc.length() != 4) {
            throw new IllegalArgumentException("FourCC must be four characters long");
        }
        for (final char c : fourcc.toCharArray()) {
            if (c < 32 || c > 126) {
                throw new IllegalArgumentException("FourCC must be ASCII printable");
            }
        }
        int val = 0;
        for (int i = 0; i < 4; i++) {
            val <<= 8;
            val |= fourcc.charAt(3 - i);
        }
        this.value = val;
    }

    /**
     * Return FourCC int value.
     *
     * @return int value.
     */
    public int toInt() {
        return value;
    }

    /**
     * @see java.lang.Object#toString()
     */
    @Override
    public String toString() {
        final var stringBuf = new StringBuffer();
        stringBuf.append((char) ((value >> 24) & 0xFF)).append((char) ((value >> 16) & 0xFF))
                .append((char) ((value >> 8) & 0xFF)).append((char) (value & 0xFF));
        return stringBuf.toString();
    }
}
