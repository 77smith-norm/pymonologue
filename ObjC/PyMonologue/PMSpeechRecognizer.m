#import "PMSpeechRecognizer.h"

static NSString * const PMSpeechRecognizerErrorDomain = @"com.rastreus.pymonologue.speech";

@interface PMSpeechRecognizer ()
@property (nonatomic, copy) NSString *localeIdentifier;
@property (nonatomic, readwrite) BOOL isAvailable;
@end

@implementation PMSpeechRecognizer

- (instancetype)init {
    return [self initWithLocale:@"en-US"];
}

- (instancetype)initWithLocale:(NSString *)localeIdentifier {
    self = [super init];
    if (self) {
        _localeIdentifier = [localeIdentifier copy] ?: @"en-US";
        _isAvailable = NO;
    }
    return self;
}

- (void)transcribeAudioFileAtPath:(NSString *)path
                       completion:(void (^)(NSString *transcript, NSError *error))completion {
    if (completion == nil) {
        return;
    }

    NSDictionary *userInfo = @{
        NSLocalizedDescriptionKey: @"device smoke test required",
        NSLocalizedFailureReasonErrorKey: @"SFSpeechRecognizer must be verified on iPhone 11 Pro Max inside the Pythonista keyboard context.",
        @"localeIdentifier": self.localeIdentifier ?: @"en-US",
        @"audioPath": path ?: @"",
    };
    NSError *error = [NSError errorWithDomain:PMSpeechRecognizerErrorDomain code:1 userInfo:userInfo];
    completion(nil, error);
}

@end
