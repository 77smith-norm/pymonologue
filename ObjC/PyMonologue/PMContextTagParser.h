#import <Foundation/Foundation.h>

@interface PMContextTagParser : NSObject

- (NSDictionary *)parseTags:(NSString *)text;
- (NSString *)stripTags:(NSString *)text;
- (NSString *)prependTags:(NSDictionary *)tags toText:(NSString *)text;

@end
