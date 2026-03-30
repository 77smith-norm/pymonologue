#import <XCTest/XCTest.h>

#import "PMTextNormalizer.h"

@interface PMTextNormalizerTests : XCTestCase
@property (nonatomic, strong) PMTextNormalizer *normalizer;
@end

@implementation PMTextNormalizerTests

- (void)setUp {
    [super setUp];
    self.normalizer = [[PMTextNormalizer alloc] init];
}

- (void)testStripsURLs {
    XCTAssertEqualObjects([self.normalizer normalize:@"check https://example.com for details"], @"Check for details.");
}

- (void)testStripsHTTPURL {
    XCTAssertEqualObjects([self.normalizer normalize:@"visit http://test.com now"], @"Visit now.");
}

- (void)testStripsPhoneNumbers {
    XCTAssertEqualObjects([self.normalizer normalize:@"call 555-123-4567 tomorrow"], @"Call tomorrow.");
}

- (void)testStripsPhoneNumbersWithDots {
    XCTAssertEqualObjects([self.normalizer normalize:@"phone 555.123.4567"], @"Phone.");
}

- (void)testStripsPlainPhoneNumbers {
    XCTAssertEqualObjects([self.normalizer normalize:@"number is 5551234567"], @"Number is.");
}

- (void)testCollapsesWhitespace {
    XCTAssertEqualObjects([self.normalizer normalize:@"lots    of   spaces"], @"Lots of spaces.");
}

- (void)testCollapsesLeadingAndTrailingWhitespace {
    XCTAssertEqualObjects([self.normalizer normalize:@"  hello world  "], @"Hello world.");
}

- (void)testCollapsesRepeatedFillers {
    XCTAssertEqualObjects([self.normalizer normalize:@"um um um this is ridiculous um"], @"Um this is ridiculous um.");
}

- (void)testPreservesSingleFiller {
    XCTAssertEqualObjects([self.normalizer normalize:@"um I think we should go"], @"Um I think we should go.");
}

- (void)testPreservesTwoFillers {
    XCTAssertEqualObjects([self.normalizer normalize:@"um um I think we should go"], @"Um um I think we should go.");
}

- (void)testCapitalizesFirstLetter {
    XCTAssertEqualObjects([self.normalizer normalize:@"hello world"], @"Hello world.");
}

- (void)testPreservesExistingQuestionMark {
    XCTAssertEqualObjects([self.normalizer normalize:@"is this working?"], @"Is this working?");
}

- (void)testPreservesExistingExclamationPoint {
    XCTAssertEqualObjects([self.normalizer normalize:@"it works!"], @"It works!");
}

- (void)testEmptyString {
    XCTAssertEqualObjects([self.normalizer normalize:@""], @"");
}

- (void)testNilRaises {
    XCTAssertThrowsSpecificNamed([self.normalizer normalize:(NSString *)nil], NSException, NSInvalidArgumentException);
}

- (void)testSingleWordWithPunctuation {
    XCTAssertEqualObjects([self.normalizer normalize:@"hello!"], @"Hello!");
}

- (void)testUnicodePreserved {
    XCTAssertEqualObjects([self.normalizer normalize:@"café"], @"Café.");
}

- (void)testMultipleURLs {
    XCTAssertEqualObjects([self.normalizer normalize:@"visit https://a.com and http://b.com ok"], @"Visit and ok.");
}

@end
