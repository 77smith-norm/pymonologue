#import "PMTextNormalizer.h"

@interface PMTextNormalizer ()
- (NSString *)replacePattern:(NSString *)pattern
                    inString:(NSString *)string
                withTemplate:(NSString *)templateString
                     options:(NSRegularExpressionOptions)options;
- (NSString *)capitalizeFirstLetterInString:(NSString *)string;
- (BOOL)hasTerminalPunctuation:(NSString *)string;
@end

@implementation PMTextNormalizer

- (instancetype)init {
    self = [super init];
    return self;
}

- (NSString *)normalize:(NSString *)text {
    if (text == nil) {
        [NSException raise:NSInvalidArgumentException format:@"text cannot be nil"];
    }
    if (text.length == 0) {
        return text;
    }

    NSString *normalized = [self replacePattern:@"https?://\\S+"
                                       inString:text
                                   withTemplate:@""
                                        options:0];
    normalized = [self replacePattern:@"\\b\\d{3}[-.]?\\d{3}[-.]?\\d{4}\\b"
                             inString:normalized
                         withTemplate:@""
                              options:0];
    normalized = [self replacePattern:@"\\s+"
                             inString:normalized
                         withTemplate:@" "
                              options:0];
    normalized = [normalized stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
    if (normalized.length == 0) {
        return normalized;
    }

    normalized = [self replacePattern:@"\\b(um|uh|like|you know|I mean)\\b(?:\\s+\\1\\b){2,}"
                             inString:normalized
                         withTemplate:@"$1"
                              options:NSRegularExpressionCaseInsensitive];
    if (normalized.length == 0) {
        return normalized;
    }

    normalized = [self capitalizeFirstLetterInString:normalized];
    if (![self hasTerminalPunctuation:normalized]) {
        normalized = [normalized stringByAppendingString:@"."];
    }

    return normalized;
}

- (NSString *)replacePattern:(NSString *)pattern
                    inString:(NSString *)string
                withTemplate:(NSString *)templateString
                     options:(NSRegularExpressionOptions)options {
    NSError *error = nil;
    NSRegularExpression *expression = [NSRegularExpression regularExpressionWithPattern:pattern options:options error:&error];
    NSAssert(expression != nil && error == nil, @"Invalid regex pattern: %@", pattern);
    return [expression stringByReplacingMatchesInString:string options:0 range:NSMakeRange(0, string.length) withTemplate:templateString];
}

- (NSString *)capitalizeFirstLetterInString:(NSString *)string {
    if (string.length == 0) {
        return string;
    }

    NSRange firstRange = [string rangeOfComposedCharacterSequenceAtIndex:0];
    NSString *firstCharacter = [[string substringWithRange:firstRange] uppercaseString];
    NSString *rest = [string substringFromIndex:NSMaxRange(firstRange)];
    return [firstCharacter stringByAppendingString:rest];
}

- (BOOL)hasTerminalPunctuation:(NSString *)string {
    if (string.length == 0) {
        return NO;
    }

    unichar lastCharacter = [string characterAtIndex:string.length - 1];
    return lastCharacter == '.' || lastCharacter == '!' || lastCharacter == '?';
}

@end
