function sprintf(format, ...args) {
    let argIndex = 0;
    
    return format.replace(/%(?:(\d+)\$)?([+\-0 #]*)(\*|\d+)?(?:\.(\*|\d+))?([hlL])?([diouxXeEfFgGaAcspn%])/g, 
        function(match, position, flags, width, precision, length, specifier) {
            // Handle literal %
            if (specifier === '%') {
                return '%';
            }
            
            // Get the argument
            let arg;
            if (position) {
                arg = args[parseInt(position) - 1];
            } else {
                arg = args[argIndex++];
            }
            
            // Parse flags
            const leftAlign = flags.includes('-');
            const showSign = flags.includes('+');
            const spaceForSign = flags.includes(' ');
            const padWithZeros = flags.includes('0') && !leftAlign;
            const alternate = flags.includes('#');
            
            // Parse width
            let minWidth = 0;
            if (width === '*') {
                minWidth = args[argIndex++];
            } else if (width) {
                minWidth = parseInt(width);
            }
            
            // Parse precision
            let prec = -1;
            if (precision === '*') {
                prec = args[argIndex++];
            } else if (precision) {
                prec = parseInt(precision);
            }
            
            let result = '';
            
            switch (specifier) {
                case 'd':
                case 'i':
                    result = formatInteger(arg, 10, false, showSign, spaceForSign);
                    break;
                    
                case 'o':
                    result = formatInteger(arg, 8, false, false, false);
                    if (alternate && result !== '0' && !result.startsWith('0')) {
                        result = '0' + result;
                    }
                    break;
                    
                case 'u':
                    result = formatInteger(arg, 10, true, false, false);
                    break;
                    
                case 'x':
                    result = formatInteger(arg, 16, true, false, false).toLowerCase();
                    if (alternate && result !== '0') {
                        result = '0x' + result;
                    }
                    break;
                    
                case 'X':
                    result = formatInteger(arg, 16, true, false, false).toUpperCase();
                    if (alternate && result !== '0') {
                        result = '0X' + result;
                    }
                    break;
                    
                case 'f':
                case 'F':
                    result = formatFloat(arg, prec === -1 ? 6 : prec, showSign, spaceForSign);
                    break;
                    
                case 'e':
                    result = formatExponential(arg, prec === -1 ? 6 : prec, showSign, spaceForSign, false);
                    break;
                    
                case 'E':
                    result = formatExponential(arg, prec === -1 ? 6 : prec, showSign, spaceForSign, true);
                    break;
                    
                case 'g':
                    result = formatGeneral(arg, prec === -1 ? 6 : prec, showSign, spaceForSign, false, alternate);
                    break;
                    
                case 'G':
                    result = formatGeneral(arg, prec === -1 ? 6 : prec, showSign, spaceForSign, true, alternate);
                    break;
                    
                case 'c':
                    if (typeof arg === 'number') {
                        result = String.fromCharCode(arg);
                    } else {
                        result = String(arg).charAt(0) || '';
                    }
                    break;
                    
                case 's':
                    result = String(arg == null ? '' : arg);
                    if (prec >= 0) {
                        result = result.substring(0, prec);
                    }
                    break;
                    
                case 'p':
                    result = '0x' + (arg ? arg.toString(16) : '0');
                    break;
                    
                default:
                    result = match;
            }
            
            // Apply width formatting
            return applyWidth(result, minWidth, leftAlign, padWithZeros);
        }
    );
    
    function formatInteger(value, base, unsigned, showSign, spaceForSign) {
        let num = parseInt(value) || 0;
        
        if (unsigned && num < 0) {
            num = (num >>> 0); // Convert to unsigned 32-bit
        }
        
        let result = Math.abs(num).toString(base);
        
        if (num < 0 && !unsigned) {
            result = '-' + result;
        } else if (showSign && num >= 0) {
            result = '+' + result;
        } else if (spaceForSign && num >= 0) {
            result = ' ' + result;
        }
        
        return result;
    }
    
    function formatFloat(value, precision, showSign, spaceForSign) {
        let num = parseFloat(value) || 0;
        let result = num.toFixed(precision);
        
        if (num >= 0) {
            if (showSign) {
                result = '+' + result;
            } else if (spaceForSign) {
                result = ' ' + result;
            }
        }
        
        return result;
    }
    
    function formatExponential(value, precision, showSign, spaceForSign, uppercase) {
        let num = parseFloat(value) || 0;
        let result = num.toExponential(precision);
        
        if (uppercase) {
            result = result.toUpperCase();
        }
        
        if (num >= 0) {
            if (showSign) {
                result = '+' + result;
            } else if (spaceForSign) {
                result = ' ' + result;
            }
        }
        
        return result;
    }
    
    function formatGeneral(value, precision, showSign, spaceForSign, uppercase, alternate) {
        let num = parseFloat(value) || 0;
        
        // Choose between fixed and exponential notation
        let exp = Math.floor(Math.log10(Math.abs(num)));
        let useExp = exp < -4 || exp >= precision;
        
        let result;
        if (useExp) {
            result = num.toExponential(precision - 1);
        } else {
            result = num.toPrecision(precision);
        }
        
        // Remove trailing zeros unless alternate flag is set
        if (!alternate) {
            result = result.replace(/\.?0+$/, '');
            result = result.replace(/\.?0+e/, 'e');
        }
        
        if (uppercase) {
            result = result.toUpperCase();
        }
        
        if (num >= 0) {
            if (showSign) {
                result = '+' + result;
            } else if (spaceForSign) {
                result = ' ' + result;
            }
        }
        
        return result;
    }
    
    function applyWidth(str, width, leftAlign, padWithZeros) {
        if (width <= str.length) {
            return str;
        }
        
        let padding = width - str.length;
        let padChar = padWithZeros ? '0' : ' ';
        
        if (leftAlign) {
            return str + ' '.repeat(padding);
        } else if (padWithZeros && (str[0] === '+' || str[0] === '-' || str[0] === ' ')) {
            return str[0] + padChar.repeat(padding) + str.substring(1);
        } else {
            return padChar.repeat(padding) + str;
        }
    }
}

export { sprintf };