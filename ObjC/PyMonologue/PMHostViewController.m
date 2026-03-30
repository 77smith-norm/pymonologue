#import "PMHostViewController.h"

@implementation PMHostViewController

static UIColor *PMHostHexColor(NSUInteger hexValue) {
    CGFloat red = ((hexValue >> 16) & 0xFF) / 255.0;
    CGFloat green = ((hexValue >> 8) & 0xFF) / 255.0;
    CGFloat blue = (hexValue & 0xFF) / 255.0;
    return [UIColor colorWithRed:red green:green blue:blue alpha:1.0];
}

- (void)viewDidLoad {
    [super viewDidLoad];

    self.title = @"PyMonologue";
    self.view.backgroundColor = PMHostHexColor(0x000000);

    UILabel *headline = [[UILabel alloc] init];
    headline.translatesAutoresizingMaskIntoConstraints = NO;
    headline.text = @"PyMonologue host app";
    headline.textAlignment = NSTextAlignmentCenter;
    headline.numberOfLines = 0;
    headline.textColor = UIColor.whiteColor;
    headline.font = [UIFont boldSystemFontOfSize:30.0];

    UILabel *body = [[UILabel alloc] init];
    body.translatesAutoresizingMaskIntoConstraints = NO;
    body.text = @"This app exists to host the keyboard extension. Open the custom keyboard in Settings, then run the three device smoke tests from SPEC.md on iPhone 11 Pro Max.";
    body.textAlignment = NSTextAlignmentCenter;
    body.numberOfLines = 0;
    body.textColor = PMHostHexColor(0xC8C8C8);
    body.font = [UIFont systemFontOfSize:17.0 weight:UIFontWeightRegular];

    UIView *accentBar = [[UIView alloc] init];
    accentBar.translatesAutoresizingMaskIntoConstraints = NO;
    accentBar.backgroundColor = PMHostHexColor(0x00D4AA);
    accentBar.layer.cornerRadius = 2.0;

    UIStackView *stackView = [[UIStackView alloc] initWithArrangedSubviews:@[headline, accentBar, body]];
    stackView.translatesAutoresizingMaskIntoConstraints = NO;
    stackView.axis = UILayoutConstraintAxisVertical;
    stackView.spacing = 18.0;
    stackView.alignment = UIStackViewAlignmentFill;

    [self.view addSubview:stackView];

    [NSLayoutConstraint activateConstraints:@[
        [stackView.centerYAnchor constraintEqualToAnchor:self.view.centerYAnchor],
        [stackView.leadingAnchor constraintEqualToAnchor:self.view.leadingAnchor constant:28.0],
        [stackView.trailingAnchor constraintEqualToAnchor:self.view.trailingAnchor constant:-28.0],
        [accentBar.heightAnchor constraintEqualToConstant:4.0],
        [accentBar.widthAnchor constraintEqualToConstant:88.0],
    ]];
}

@end
