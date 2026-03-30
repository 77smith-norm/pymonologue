#import "PMContextTagParser.h"

@interface PMContextTagParser ()
- (NSRegularExpression *)tagExpression;
- (NSArray<NSString *> *)orderedKeysForTags:(NSDictionary<NSString *, NSString *> *)tags;
@end

@implementation PMContextTagParser

- (NSDictionary *)parseTags:(NSString *)text {
    if (text.length == 0) {
        return @{};
    }

    NSMutableDictionary<NSString *, NSString *> *result = [NSMutableDictionary dictionary];
    NSRegularExpression *expression = [self tagExpression];
    NSArray<NSTextCheckingResult *> *matches = [expression matchesInString:text options:0 range:NSMakeRange(0, text.length)];

    for (NSTextCheckingResult *match in matches) {
        NSRange keyRange = [match rangeAtIndex:1];
        NSRange valueRange = [match rangeAtIndex:2];
        NSRange freeformRange = [match rangeAtIndex:3];

        if (keyRange.location != NSNotFound && valueRange.location != NSNotFound) {
            NSString *key = [text substringWithRange:keyRange];
            NSString *value = [text substringWithRange:valueRange];
            result[key] = value;
        } else if (freeformRange.location != NSNotFound) {
            NSString *key = [text substringWithRange:freeformRange];
            result[key] = @"";
        }
    }

    return result.copy;
}

- (NSString *)stripTags:(NSString *)text {
    if (text.length == 0) {
        return text ?: @"";
    }

    NSRegularExpression *expression = [self tagExpression];
    NSString *stripped = [expression stringByReplacingMatchesInString:text options:0 range:NSMakeRange(0, text.length) withTemplate:@""];
    return [stripped stringByTrimmingCharactersInSet:[NSCharacterSet whitespaceAndNewlineCharacterSet]];
}

- (NSString *)prependTags:(NSDictionary *)tags toText:(NSString *)text {
    NSString *resolvedText = text ?: @"";
    if (tags.count == 0) {
        return resolvedText;
    }

    NSMutableString *tagString = [NSMutableString string];
    for (NSString *key in [self orderedKeysForTags:tags]) {
        NSString *value = tags[key];
        if (value.length > 0) {
            [tagString appendFormat:@"[%@:%@]", key, value];
        } else {
            [tagString appendFormat:@"[%@]", key];
        }
    }

    return [NSString stringWithFormat:@"%@ %@", tagString, resolvedText];
}

- (NSRegularExpression *)tagExpression {
    static NSRegularExpression *expression = nil;
    static dispatch_once_t onceToken;
    dispatch_once(&onceToken, ^{
        expression = [NSRegularExpression regularExpressionWithPattern:@"\\[([a-z]+):([^\\]]+)\\]|\\[([a-z]+)\\]" options:0 error:nil];
    });
    return expression;
}

- (NSArray<NSString *> *)orderedKeysForTags:(NSDictionary<NSString *, NSString *> *)tags {
    NSMutableArray<NSString *> *ordered = [NSMutableArray array];
    for (NSString *knownKey in @[@"project", @"task", @"priority"]) {
        if (tags[knownKey] != nil) {
            [ordered addObject:knownKey];
        }
    }

    NSMutableArray<NSString *> *otherKeys = [NSMutableArray array];
    for (NSString *key in tags) {
        if (![ordered containsObject:key]) {
            [otherKeys addObject:key];
        }
    }
    [otherKeys sortUsingSelector:@selector(localizedCaseInsensitiveCompare:)];
    [ordered addObjectsFromArray:otherKeys];
    return ordered.copy;
}

@end
