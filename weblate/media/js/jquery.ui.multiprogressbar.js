/*jslint white: true vars: true browser: true todo: true */
/*jshint camelcase:true, plusplus:true, forin:true, noarg:true, noempty:true, eqeqeq:true, bitwise:true, strict:true, undef:true, unused:true, curly:true, browser:true, devel:true, maxerr:100, white:false, onevar:false */
/*global jQuery:true $:true */

/* jQuery UI Multi-Progress Bar 1.0
 * http://github.com/j-ulrich/jquery-ui-multiprogressbar
 *
 * Copyright (c) 2012 Jochen Ulrich <jochenulrich@t-online.de>
 * Licensed under the MIT license (MIT-LICENSE.txt).
 */

/**
 * @file jQuery UI Multi-Progress Bar
 * @version 1.0
 * @copyright 2012 Jochen Ulrich
 * @license MIT (MIT-LICENSE.txt)
 */

(function($) {
	
	/**
	 * Constructs a multiprogressbar.
	 * @name multiprogressbar
	 * @public
	 * @function
	 * @memberOf jQuery.ui
	 */
	$.widget("ui.multiprogressbar", 
	
	/**
	 * @lends jQuery.ui.multiprogressbar.prototype
	 */
	{
		
		// Options
		/**
		 * Default values of the options.
		 * @since 1.0
		 */
		options: {
			parts: [{value: 0, barClass: "", text: false, textClass: ""}]
		},
		
		/**
		 * Constructor for multiprogressbars.
		 * @private
		 * @author julrich
		 * @since 1.0
		 */
		_create: function() {
			var self = this;
			self.element.progressbar({value: 0, disabled: self.options.disabled}); // Creates one part with width 0%
			self.element.addClass("ui-multiprogressbar");
			
			// Use the part generated by jQuery UI progressbar as template for the other parts
			self._partTemplate = self._getPartElements().outerHTML();
			self._createParts(self.options.parts);
			$.extend(self,{
				created: true
			});
		},
		
		/**
		 * @returns {Object} a jQuery object containing all part elements.
		 * @private
		 * @author julrich
		 * @since 1.0
		 */
		_getPartElements: function() {
			return this.element.children(".ui-progressbar-value");
		},
		
		/**
		 * (Re)creates the markup of the parts.
		 * @param {Array} parts - Array of part objects defining the properties of the parts to be created.
		 * @fires multiprogressbar#change when the function is called <b>after</b> the creation of the multiprogressbar
		 * (i.e. the event is not fired during the creation).
		 * @fires multiprogressbar#complete when the total progress reaches or exceeds 100%.
		 * @private
		 * @author julrich
		 * @since 1.0
		 */
		_createParts: function(parts) {
			var self = this;
			
			self._getPartElements().remove(); // Remove all existing parts and then rebuild them
			var first = true;
			var lastVisibleElement = null;
			var totalValue = 0;
			$.each(parts, function(i, part) {
				var partElement = $(self._partTemplate).appendTo(self.element);
				
				if (first === false) {
					partElement.removeClass("ui-corner-left");
				}
				if (part.value > 0 && totalValue < 100) {
					first = false;
					// Check if the part would exceed the 100% and cut it at 100%
					part.value = totalValue+part.value > 100 ? 100-totalValue : part.value; 
					partElement.css('width', part.value+"%").show();
					lastVisibleElement = partElement;
					totalValue += part.value;
				}
				else {
					// Hide part if the progress is <= 0 or if we exceeded 100% already 
					part.value = 0;
					partElement.hide();
				}
				
				partElement.addClass(part.barClass);
				
				if (part.text !== undefined && part.text !== null && part.text !== false) {
					var textForPart;
					if (part.text === true) {
						textForPart = Math.round(part.value)+"%";
					}
					else if ($.trim(part.text) !== "") {
						textForPart = part.text;
					}
					$('<div></div>').addClass("ui-multiprogressbar-valuetext").text(textForPart).addClass(part.textClass).appendTo(partElement);
				}
			});
			if (self.created === true) { // Don't trigger "change" when we are creating the progressbar for the first time 
				self._trigger("change", null, {parts: parts});
			}
			if (totalValue >= 99.9) {
				lastVisibleElement.addClass("ui-corner-right");
				// Trigger complete
				self._trigger("complete");
			}
		},
		
		/**
		 * Restores the element to it's original state.
		 * @public
		 * @author julrich
		 * @since 1.0
		 */
		destroy: function() {
			var self = this;
			self._getPartElements().remove();
			self.element.progressbar("destroy");
		},
		
		/**
		 * Changes an option.
		 * @param {String} option - name of the option to be set.
		 * @param value - new value for the option.
		 * @private
		 * @author julrich
		 * @since 1.0
		 */
		_setOption: function(option, value) {
			var self = this;
			$.Widget.prototype._setOption.apply( self, arguments );
			
			switch(option) {
			case "parts":
				self._createParts(value);
				break;
			}
		},
		
		/**
		 * @return {Numeric} the sum of the progress of all visible parts.
		 * <b>Note:</b> When the sum of the progress of the parts exceeds 100, the progress
		 * will be truncated at 100 and the value of successive parts will be set to 0. This means
		 * that this function will always return a value in the range [0,100].
		 * @public
		 * @author julrich
		 * @since 1.0
		 */
		total: function() {
			var self = this;
			var totalValue = 0;
			$.each(self.options.parts, function(i, part) {
				totalValue += part.value;
			});
			
			return totalValue;
		}
	});
}(jQuery));