/*
 * Copyright (c) Steven P. Goldsmith. All rights reserved.
 *
 * Created by Steven P. Goldsmith on December 22, 2013
 * sgjava@gmail.com
 */
package com.codeferm.opencv;

import java.awt.AWTEvent;
import java.awt.Frame;
import java.awt.event.AWTEventListener;
import java.awt.event.KeyEvent;

/**
 * Frame that listens for keyboard input.
 *
 * @author sgoldsmith
 * @version 1.0.0
 * @since 1.0.0
 */
public class KeyEventFrame extends Frame implements AWTEventListener {
    /**
     * Serializable class version number.
     */
    private static final long serialVersionUID = -2980614343410118496L;

    /**
     * Add key event to AWT event listener.
     */
    public KeyEventFrame() {
        super("Java Capture");
        this.getToolkit().addAWTEventListener(this, AWTEvent.KEY_EVENT_MASK);
    }

    /**
     * Handle key events and exit if escape pressed.
     *
     * @param event
     *            AWT event.
     */
    @Override
    public final void eventDispatched(final AWTEvent event) {
        if (event instanceof KeyEvent) {
            final var key = (KeyEvent) event;
            // Handle key presses
            if (key.getID() == KeyEvent.KEY_PRESSED) {
                // Exit if escape pressed
                if (key.getKeyChar() == KeyEvent.VK_ESCAPE) {
                    key.consume();
                    System.exit(0);
                }
                key.consume();
            }
        }
    }
}
