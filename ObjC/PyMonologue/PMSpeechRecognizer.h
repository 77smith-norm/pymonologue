#import <Foundation/Foundation.h>

@interface PMSpeechRecognizer : NSObject

@property (nonatomic, readonly) BOOL isAvailable;

- (instancetype)initWithLocale:(NSString *)localeIdentifier;
- (void)transcribeAudioFileAtPath:(NSString *)path
                       completion:(void (^)(NSString *transcript, NSError *error))completion;

@end
