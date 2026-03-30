#import "PMKeyboardViewController.h"

#import <QuartzCore/QuartzCore.h>

#import "PMContextTagParser.h"
#import "PMSpeechRecognizer.h"
#import "PMTextNormalizer.h"

static UIColor *PMKeyboardHexColor(NSUInteger hexValue) {
    CGFloat red = ((hexValue >> 16) & 0xFF) / 255.0;
    CGFloat green = ((hexValue >> 8) & 0xFF) / 255.0;
    CGFloat blue = (hexValue & 0xFF) / 255.0;
    return [UIColor colorWithRed:red green:green blue:blue alpha:1.0];
}

@interface PMKeyboardViewController ()
@property (nonatomic, strong) CAGradientLayer *backgroundLayer;
@property (nonatomic, strong) UIButton *tagsButton;
@property (nonatomic, strong) UIButton *voiceButton;
@property (nonatomic, strong) UIButton *nextKeyboardButton;
@property (nonatomic, strong) UIButton *spaceButton;
@property (nonatomic, strong) UIButton *returnButton;
@property (nonatomic, assign, getter=isRecording) BOOL recording;
@property (nonatomic, strong) PMSpeechRecognizer *speechRecognizer;
@property (nonatomic, strong) PMTextNormalizer *textNormalizer;
@property (nonatomic, strong) PMContextTagParser *tagParser;
@end

@implementation PMKeyboardViewController

- (void)viewDidLoad {
    [super viewDidLoad];

    self.speechRecognizer = [[PMSpeechRecognizer alloc] initWithLocale:@"en-US"];
    self.textNormalizer = [[PMTextNormalizer alloc] init];
    self.tagParser = [[PMContextTagParser alloc] init];

    self.view.backgroundColor = UIColor.blackColor;
    [self configureBackgroundLayer];
    [self configureKeyboardUI];
    [self updateVoiceButtonAppearance];
}

- (void)viewDidLayoutSubviews {
    [super viewDidLayoutSubviews];
    self.backgroundLayer.frame = self.view.bounds;
}

- (void)configureBackgroundLayer {
    self.backgroundLayer = [CAGradientLayer layer];
    self.backgroundLayer.colors = @[
        (__bridge id)PMKeyboardHexColor(0x000000).CGColor,
        (__bridge id)PMKeyboardHexColor(0x1A1A1A).CGColor,
    ];
    self.backgroundLayer.startPoint = CGPointMake(0.5, 0.0);
    self.backgroundLayer.endPoint = CGPointMake(0.5, 1.0);
    [self.view.layer insertSublayer:self.backgroundLayer atIndex:0];
}

- (void)configureKeyboardUI {
    UIStackView *topRow = [[UIStackView alloc] init];
    topRow.translatesAutoresizingMaskIntoConstraints = NO;
    topRow.axis = UILayoutConstraintAxisHorizontal;
    topRow.alignment = UIStackViewAlignmentCenter;
    topRow.spacing = 10.0;

    self.tagsButton = [self keyButtonWithTitle:@"TAGS" accent:NO];
    [self.tagsButton addTarget:self action:@selector(tagsButtonTapped:) forControlEvents:UIControlEventTouchUpInside];
    [topRow addArrangedSubview:self.tagsButton];

    UIView *spacer = [[UIView alloc] init];
    spacer.translatesAutoresizingMaskIntoConstraints = NO;
    [spacer setContentHuggingPriority:UILayoutPriorityDefaultLow forAxis:UILayoutConstraintAxisHorizontal];
    [topRow addArrangedSubview:spacer];

    UIStackView *punctuationRow = [[UIStackView alloc] init];
    punctuationRow.translatesAutoresizingMaskIntoConstraints = NO;
    punctuationRow.axis = UILayoutConstraintAxisHorizontal;
    punctuationRow.alignment = UIStackViewAlignmentFill;
    punctuationRow.spacing = 8.0;

    for (NSString *symbol in @[@".", @",", @"?", @"!", @"'"]) {
        UIButton *button = [self keyButtonWithTitle:symbol accent:NO];
        button.titleLabel.font = [UIFont boldSystemFontOfSize:18.0];
        [button.widthAnchor constraintEqualToConstant:40.0].active = YES;
        [button.heightAnchor constraintEqualToConstant:36.0].active = YES;
        [button addTarget:self action:@selector(punctuationButtonTapped:) forControlEvents:UIControlEventTouchUpInside];
        [punctuationRow addArrangedSubview:button];
    }
    [topRow addArrangedSubview:punctuationRow];

    self.voiceButton = [UIButton buttonWithType:UIButtonTypeSystem];
    self.voiceButton.translatesAutoresizingMaskIntoConstraints = NO;
    self.voiceButton.backgroundColor = PMKeyboardHexColor(0x00D4AA);
    self.voiceButton.layer.cornerRadius = 26.0;
    self.voiceButton.layer.masksToBounds = YES;
    self.voiceButton.titleLabel.font = [UIFont boldSystemFontOfSize:28.0];
    [self.voiceButton setTitleColor:UIColor.whiteColor forState:UIControlStateNormal];
    [self.voiceButton setTitle:@"TAP TO TALK" forState:UIControlStateNormal];
    [self.voiceButton addTarget:self action:@selector(voiceButtonTapped:) forControlEvents:UIControlEventTouchUpInside];

    UIStackView *bottomRow = [[UIStackView alloc] init];
    bottomRow.translatesAutoresizingMaskIntoConstraints = NO;
    bottomRow.axis = UILayoutConstraintAxisHorizontal;
    bottomRow.alignment = UIStackViewAlignmentFill;
    bottomRow.spacing = 10.0;

    self.nextKeyboardButton = [self keyButtonWithTitle:@"ABC" accent:NO];
    [self.nextKeyboardButton addTarget:self action:@selector(nextKeyboardButtonTapped:) forControlEvents:UIControlEventTouchUpInside];
    [self.nextKeyboardButton.widthAnchor constraintEqualToConstant:70.0].active = YES;

    self.spaceButton = [self keyButtonWithTitle:@"M" accent:NO];
    self.spaceButton.titleLabel.font = [UIFont boldSystemFontOfSize:18.0];
    [self.spaceButton addTarget:self action:@selector(spaceButtonTapped:) forControlEvents:UIControlEventTouchUpInside];
    [self.spaceButton.heightAnchor constraintEqualToConstant:52.0].active = YES;

    self.returnButton = [self keyButtonWithTitle:@"return" accent:NO];
    [self.returnButton addTarget:self action:@selector(returnButtonTapped:) forControlEvents:UIControlEventTouchUpInside];
    [self.returnButton.widthAnchor constraintEqualToConstant:90.0].active = YES;

    [bottomRow addArrangedSubview:self.nextKeyboardButton];
    [bottomRow addArrangedSubview:self.spaceButton];
    [bottomRow addArrangedSubview:self.returnButton];

    [self.view addSubview:topRow];
    [self.view addSubview:self.voiceButton];
    [self.view addSubview:bottomRow];

    [NSLayoutConstraint activateConstraints:@[
        [topRow.topAnchor constraintEqualToAnchor:self.view.topAnchor constant:12.0],
        [topRow.leadingAnchor constraintEqualToAnchor:self.view.leadingAnchor constant:12.0],
        [topRow.trailingAnchor constraintEqualToAnchor:self.view.trailingAnchor constant:-12.0],

        [self.voiceButton.topAnchor constraintEqualToAnchor:topRow.bottomAnchor constant:20.0],
        [self.voiceButton.centerXAnchor constraintEqualToAnchor:self.view.centerXAnchor],
        [self.voiceButton.leadingAnchor constraintGreaterThanOrEqualToAnchor:self.view.leadingAnchor constant:20.0],
        [self.voiceButton.trailingAnchor constraintLessThanOrEqualToAnchor:self.view.trailingAnchor constant:-20.0],
        [self.voiceButton.widthAnchor constraintEqualToConstant:250.0],
        [self.voiceButton.heightAnchor constraintEqualToConstant:124.0],

        [bottomRow.topAnchor constraintEqualToAnchor:self.voiceButton.bottomAnchor constant:20.0],
        [bottomRow.leadingAnchor constraintEqualToAnchor:self.view.leadingAnchor constant:12.0],
        [bottomRow.trailingAnchor constraintEqualToAnchor:self.view.trailingAnchor constant:-12.0],
        [bottomRow.bottomAnchor constraintEqualToAnchor:self.view.bottomAnchor constant:-12.0],
        [self.spaceButton.widthAnchor constraintGreaterThanOrEqualToConstant:150.0],
    ]];
}

- (UIButton *)keyButtonWithTitle:(NSString *)title accent:(BOOL)accent {
    UIButton *button = [UIButton buttonWithType:UIButtonTypeSystem];
    button.translatesAutoresizingMaskIntoConstraints = NO;
    button.backgroundColor = accent ? PMKeyboardHexColor(0x00D4AA) : PMKeyboardHexColor(0x2A2A2A);
    button.layer.cornerRadius = 14.0;
    button.layer.masksToBounds = YES;
    button.titleLabel.font = [UIFont boldSystemFontOfSize:16.0];
    [button setTitle:title forState:UIControlStateNormal];
    [button setTitleColor:UIColor.whiteColor forState:UIControlStateNormal];
    button.contentEdgeInsets = UIEdgeInsetsMake(8.0, 12.0, 8.0, 12.0);
    return button;
}

- (void)voiceButtonTapped:(id)sender {
    NSLog(@"Voice button tapped");
    if (self.isRecording) {
        [self stopRecording];
    } else {
        [self startRecording];
    }
}

- (void)startRecording {
    self.recording = YES;
    [self updateVoiceButtonAppearance];
}

- (void)stopRecording {
    self.recording = NO;
    [self updateVoiceButtonAppearance];
}

- (void)updateVoiceButtonAppearance {
    UIColor *idleColor = PMKeyboardHexColor(0x00D4AA);
    UIColor *recordingColor = PMKeyboardHexColor(0xFF453A);
    [self.voiceButton setBackgroundColor:self.isRecording ? recordingColor : idleColor];
    [self.voiceButton setTitle:(self.isRecording ? @"TAP TO STOP" : @"TAP TO TALK") forState:UIControlStateNormal];

    [self.voiceButton.layer removeAnimationForKey:@"pm_pulse"];
    if (self.isRecording) {
        CABasicAnimation *pulse = [CABasicAnimation animationWithKeyPath:@"transform.scale"];
        pulse.fromValue = @1.0;
        pulse.toValue = @1.05;
        pulse.duration = 0.75;
        pulse.autoreverses = YES;
        pulse.repeatCount = HUGE_VALF;
        pulse.timingFunction = [CAMediaTimingFunction functionWithName:kCAMediaTimingFunctionEaseInEaseOut];
        [self.voiceButton.layer addAnimation:pulse forKey:@"pm_pulse"];
    }
}

- (void)tagsButtonTapped:(id)sender {
    NSLog(@"Tags button tapped");
}

- (void)punctuationButtonTapped:(UIButton *)sender {
    [self insertText:sender.currentTitle ?: @""];
}

- (void)nextKeyboardButtonTapped:(id)sender {
    [self advanceToNextInputMode];
}

- (void)spaceButtonTapped:(id)sender {
    [self insertText:@" "];
}

- (void)returnButtonTapped:(id)sender {
    [self insertText:@"\n"];
}

- (void)insertText:(NSString *)text {
    [self.textDocumentProxy insertText:text ?: @""];
}

@end
