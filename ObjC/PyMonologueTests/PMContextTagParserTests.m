#import <XCTest/XCTest.h>

#import "PMContextTagParser.h"

@interface PMContextTagParserTests : XCTestCase
@property (nonatomic, strong) PMContextTagParser *parser;
@end

@implementation PMContextTagParserTests

- (void)setUp {
    [super setUp];
    self.parser = [[PMContextTagParser alloc] init];
}

- (void)testParseProjectTag {
    XCTAssertEqualObjects([self.parser parseTags:@"[project:cgmclaw]"], @{@"project": @"cgmclaw"});
}

- (void)testParseTaskTag {
    XCTAssertEqualObjects([self.parser parseTags:@"[task:debug]"], @{@"task": @"debug"});
}

- (void)testParsePriorityTag {
    XCTAssertEqualObjects([self.parser parseTags:@"[priority:urgent]"], @{@"priority": @"urgent"});
}

- (void)testParseFreeformTag {
    XCTAssertEqualObjects([self.parser parseTags:@"[note]"], @{@"note": @""});
}

- (void)testParseMultipleTags {
    NSString *text = @"[project:cgmclaw][task:debug] the OAuth flow is broken";
    XCTAssertEqualObjects([self.parser parseTags:text], (@{ @"project": @"cgmclaw", @"task": @"debug" }));
}

- (void)testParseAllTypes {
    NSString *text = @"[project:cgmclaw][task:debug][priority:urgent][note]";
    XCTAssertEqualObjects([self.parser parseTags:text], (@{ @"project": @"cgmclaw", @"task": @"debug", @"priority": @"urgent", @"note": @"" }));
}

- (void)testParseNoTags {
    XCTAssertEqualObjects([self.parser parseTags:@"hello world"], @{});
}

- (void)testParsePartialTag {
    XCTAssertEqualObjects([self.parser parseTags:@"[project"], @{});
}

- (void)testParseMixedContent {
    NSString *text = @"[project:cgmclaw] the OAuth token [task:debug] is broken";
    XCTAssertEqualObjects([self.parser parseTags:text], (@{ @"project": @"cgmclaw", @"task": @"debug" }));
}

- (void)testCaseSensitiveKeys {
    XCTAssertEqualObjects([self.parser parseTags:@"[PROJECT:cgmclaw]"], @{});
}

- (void)testStripSingleTag {
    XCTAssertEqualObjects([self.parser stripTags:@"[project:cgmclaw]"], @"");
}

- (void)testStripWithContent {
    XCTAssertEqualObjects([self.parser stripTags:@"[project:cgmclaw] the OAuth flow"], @"the OAuth flow");
}

- (void)testStripMultipleTags {
    XCTAssertEqualObjects([self.parser stripTags:@"[project:cgmclaw][task:debug] the OAuth flow"], @"the OAuth flow");
}

- (void)testStripNoTags {
    XCTAssertEqualObjects([self.parser stripTags:@"hello world"], @"hello world");
}

- (void)testStripNormalizesWhitespace {
    XCTAssertEqualObjects([self.parser stripTags:@"[project:cgmclaw]   hello world"], @"hello world");
}

- (void)testPrependSingleTag {
    XCTAssertEqualObjects([self.parser prependTags:@{ @"project": @"cgmclaw" } toText:@"hello"], @"[project:cgmclaw] hello");
}

- (void)testPrependMultipleTags {
    NSDictionary *tags = @{ @"task": @"debug", @"project": @"cgmclaw" };
    XCTAssertEqualObjects([self.parser prependTags:tags toText:@"hello"], @"[project:cgmclaw][task:debug] hello");
}

- (void)testPrependEmptyTags {
    XCTAssertEqualObjects([self.parser prependTags:@{} toText:@"hello"], @"hello");
}

- (void)testPrependFreeformTag {
    XCTAssertEqualObjects([self.parser prependTags:@{ @"note": @"" } toText:@"hello"], @"[note] hello");
}

@end
