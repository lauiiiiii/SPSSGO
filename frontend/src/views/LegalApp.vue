<template>
  <div class="legal-page">
    <nav class="legal-nav">
      <a href="/" class="legal-nav-logo">
        <img src="/logo.png" alt="SPSSGO" />
      </a>
      <a href="/" class="legal-back">&larr; 返回首页</a>
    </nav>
    <div class="legal-container">
      <div class="legal-tabs">
        <button :class="{ active: tab === 'terms' }" @click="tab = 'terms'">用户服务协议</button>
        <button :class="{ active: tab === 'privacy' }" @click="tab = 'privacy'">隐私政策</button>
        <button :class="{ active: tab === 'license' }" @click="tab = 'license'">开源协议</button>
      </div>

      <!-- 用户服务协议 -->
      <div v-if="tab === 'terms'" class="legal-content">
        <h1>SPSSGO 用户服务协议</h1>
        <p class="legal-meta">发布日期：2026.03.31</p>
        <p class="legal-submeta">产品全称：Smart Processing Statistical System Guided Operations</p>
        <p class="legal-owner">运营主体：日照广泰佳和网络科技有限公司</p>

        <p><strong>【审慎阅读】</strong>请您仔细阅读、充分理解本协议内容，特别是免除或者限制责任的条款、法律适用和争议解决条款，若您是18周岁以下的未成年人，您应在法定监护人监护、指导下阅读本协议使用我们服务。如您对本协议内容有任何疑问的，请勿进行下一步操作。您可以通过本平台中的联系方式向我们咨询，以便我们为您解释和说明。您通过页面点击或其他方式确认即表示您已同意本协议。</p>

        <p><strong>【签约动作】</strong>当您按照登录页面阅读并同意（点击"我接受"按钮）本协议且完成全部登录程序后，即表示您已充分阅读、理解并接受本协议的全部内容，并与本平台达成一致，成为本平台的"用户"。在阅读本协议的过程中，如果您不同意本协议或其中任何条款约定，请您立即停止注册程序，不要点击"我接受"按钮，这也意味着您将不能使用网站的服务及网站中的任何信息。</p>

        <h2>一、服务协议的确认</h2>
        <p>1. 本《服务协议》（以下简称本协议）为您（以下简称"用户"或"您"）与 SPSSGO 平台运营方（日照广泰佳和网络科技有限公司，以下简称"SPSSGO""本平台"或"我们"）就本平台为您提供技术服务所达成的协议。</p>
        <p>2. 本协议项下，SPSSGO 经营者可能根据平台的业务调整而发生变更，变更后的经营者与您共同履行本协议并向您提供服务，经营者的变更不会影响您本协议项下的权益。发生争议时，您可根据您具体使用的服务及对您权益产生影响的具体行为对象确定与您履约的主体及争议相对方。</p>
        <p>3. 由于互联网高速发展，您与本平台签署的服务协议列明的条款并不能完整罗列并覆盖您与本平台所有权利与义务，现有的约定也不能保证完全符合未来发展的需求。因此，本平台的《隐私政策》及其他各类规则为本协议的补充协议，与本协议不可分割且具有同等法律效力。如您使用 SPSSGO 服务，视为您同意上述补充协议。</p>
        <p>4. 根据国家法律法规变化、运营需要或为提升服务质量的目的，SPSSGO 将在必要的时候对上述各项协议、条款与规则进行修改更新，并通过在平台网页发出公告、通知等合理、醒目的方式向您进行提前通知。您应当及时查阅并了解相关更新修改内容，如您不同意相关更新修改内容，可停止使用相关更新修改内容所涉及的服务，此情形下，变更事项对您不产生效力；如您在上述更新修改内容实施后继续使用所涉及的服务，将视为您已同意各项更新修改内容。</p>

        <h2>二、用户资格及注册</h2>
        <p>1. 用户应为具有完全民事权利能力和民事行为能力的自然人、法人，或是能够独立承担民事责任的其他组织。用户若不具有前述规定的法律能力，须经法定代理人同意或由法定代理人代理，或是得到有权主体授权后进行注册。</p>
        <p>2. 用户注册时须提供完整、真实、准确、最新的个人资料，若您提供任何错误、不实、过时或不完整的资料，并为 SPSSGO 所确知，或 SPSSGO 有合理理由怀疑前述资料为错误、不实、过时或不完整的，SPSSGO 有权在任何时候暂停或终止您的帐号，并拒绝您现在或将来使用全部或部分服务。</p>
        <p>3. 您注册的账户名称，如存在包括但不限于违反法律法规、损害国家荣誉和利益、损害公众利益、危害国家安全、煽动民族仇恨、民族歧视、破坏民族团结、宣扬邪教和封建迷信、散布谣言、扰乱社会秩序、散布淫秽、色情、赌博、暴力、凶杀、恐怖或者教唆犯罪、侮辱或者诽谤他人、侵害他人合法权益等情形的，SPSSGO 有权随时不经通知终止您的账户。</p>
        <p>4. 若用户已经注册了账户并使用了相关服务，则用户需提供完整准确的注册信息，并及时进行更新。</p>
        <p>5. SPSSGO 对用户使用本平台服务的行为不承担任何责任，即用户需自行对使用本平台服务的行为及由此导致的任何结果承担风险，包括但不限于以下情形：</p>
        <ul>
          <li>您通过本平台使用数据分析结果可能无法准确反映真实情况甚至偏离；</li>
          <li>您通过本平台服务链接到的任何第三方网站的安全性可能存在风险；</li>
          <li>其他第三方可能通过本平台收集、使用您的个人信息；</li>
          <li>与我们提供的服务无关的其他风险。</li>
        </ul>
        <p>6. 因互联网行业的特殊性，本平台服务以"按现状"和"按可得到"的基础提供。SPSSGO 不保证服务不会受到网络中断的影响，对服务的及时性、安全性、准确性不作担保。</p>
        <p>7. 您一旦注册成功便成为本平台的用户，并将得到一个唯一的帐号，该帐号是用户身份识别的依据，您有义务自行妥善保管并保证密码和帐号的安全。</p>
        <p>8. 您使用帐号和密码进行的任何操作、发出的指令视为您本人作出。因您自身原因造成的帐号、密码等信息被冒用、盗用或非法使用，由此造成的风险和损失由您自行承担。</p>
        <p>9. 用户有权随时终止使用本平台服务并按照本平台的流程注销帐号，如您无法自行注销帐户可联系我们申请注销帐号。帐号注销后用户将无法继续使用本平台服务，且用户与本平台之间的权利义务将终止，同时还可能产生以下后果：</p>
        <ul>
          <li>如用户在注销前存在违约、侵权等不当行为或未完结合同的，用户仍应承担相应责任；</li>
          <li>一旦注销成功，帐号历史记录等将无法恢复或提供。</li>
        </ul>

        <h2>三、用户信息保护</h2>
        <p>1. 本平台仅在用户注册时，基于用户帐户安全、平台协助保障用户相应权益等需要，需要收集用户的电子邮箱等必要的用户数据，除此之外，本平台不会收集任何用户信息。用户同意本平台基于上述目的及范围收集信息。</p>
        <p>2. 本平台对收集的用户信息中涉及识别用户个人身份和用户个人隐私的信息进行保护，不会将用户的上述信息对外公开或提供给任何第三方，但以下情况除外：</p>
        <ul>
          <li>用户同意让第三方共享资料；</li>
          <li>用户同意公开其个人资料，享受为其提供的产品和服务；</li>
          <li>根据法律法规的规定，或行政机关、司法机关的要求进行披露；</li>
          <li>为了用户利益需要而向第三方提供的；</li>
          <li>基于保护用户个人隐私的需要，本平台将按照公示的隐私政策对用户隐私信息进行保护。</li>
        </ul>

        <h2>四、服务内容</h2>
        <p>1. 我们会尽一切努力让您使用服务的过程更加便捷和顺利，但鉴于技术上的问题和困难具有不可预见性，可能会导致数据丢失或服务中断。为此，您理解和同意，您使用"服务"的风险由您自行承担。我们不保证服务不会受到网络中断的影响，对服务的及时性、安全性、准确性不作任何形式的保证。</p>
        <p>2. 您知晓并认可，您存储在我们服务器上数据的公开级别完全由您自己设置，我们在未经您允许的情况下不会擅自更改其设置，对于您设置为不公开的信息，我们不会擅自泄漏给任何第三方。</p>

        <h2>五、用户使用规范</h2>
        <p>1. 用户在使用 SPSSGO 的服务时，必须遵守《网络安全法》等中华人民共和国相关法律法规的规定，用户应同意将不会利用本平台进行任何违法或不正当的活动，包括但不限于下列行为：</p>
        <p>（1）上载、展示、张贴、传播或以其它方式传送含有下列内容之一的信息：</p>
        <ul>
          <li>反对宪法所确定的基本原则的；</li>
          <li>危害国家安全，泄露国家秘密，颠覆国家政权，破坏国家统一的；</li>
          <li>损害国家荣誉和利益的；</li>
          <li>煽动民族仇恨、民族歧视、破坏民族团结的；</li>
          <li>破坏国家宗教政策，宣扬邪教和封建迷信的；</li>
          <li>散布谣言，扰乱社会秩序，破坏社会稳定的；</li>
          <li>散布淫秽、色情、赌博、暴力、凶杀、恐怖或者教唆犯罪的；</li>
          <li>侮辱或者诽谤他人，侵害他人合法权利的；</li>
          <li>含有虚假、有害、胁迫、侵害他人隐私、骚扰、侵害、中伤、粗俗、猥亵、或其它道德上令人反感的内容；</li>
          <li>含有中国法律、法规、规章、条例以及任何具有法律效力之规范所限制或禁止的其它内容的。</li>
        </ul>
        <p>（2）不得为任何非法目的而使用网络服务系统；</p>
        <p>（3）不利用 SPSSGO 的服务从事以下活动：</p>
        <ul>
          <li>未经允许，进入计算机信息网络或者使用计算机信息网络资源的；</li>
          <li>未经允许，对计算机信息网络功能进行删除、修改或者增加的；</li>
          <li>未经允许，对进入计算机信息网络中存储、处理或者传输的数据和应用程序进行删除、修改或者增加的；</li>
          <li>故意制作、传播计算机病毒等破坏性程序的；</li>
          <li>其他危害计算机信息网络安全的行为。</li>
        </ul>
        <p>2. 用户违反本协议相关规定，导致或产生的任何第三方主张的任何索赔、要求或损失，包括合理的律师费，您同意赔偿 SPSSGO 与合作公司、关联公司，并使之免受损害。对此，SPSSGO 有权视用户的行为性质，采取包括但不限于删除用户发布信息内容、暂停使用许可、终止服务、限制使用、回收服务帐号、追究法律责任等措施。</p>
        <p>3. 用户不得对本平台任何部分或本平台之使用或获得，进行复制、拷贝、出售、转售或用于任何其它商业目的。</p>
        <p>4. 用户须对自己在使用 SPSSGO 服务过程中的行为承担法律责任。用户承担法律责任的形式包括但不限于：对受到侵害者进行赔偿，以及在 SPSSGO 首先承担了因用户行为导致的行政处罚或侵权损害赔偿责任后，用户应给予 SPSSGO 等额的赔偿。</p>

        <h2>六、平台权利及义务</h2>
        <p>1. SPSSGO 有权对平台功能进行升级和改造，有权基于服务的稳定对相关服务器进行停机维护，SPSSGO 在行使以上权利时，将尽力不对用户的使用造成影响。若影响用户使用的，会提前在网站予以公告。</p>
        <p>2. SPSSGO 有权记录用户的相关数据行为，有权对用户行为是否合法进行监督和检查。若发现用户违反国家相关法律法规规定或 SPSSGO 平台相关规则的，有权采取包括冻结帐号、永久封禁、拒绝服务等措施。</p>
        <p>3. 自觉遵守相关法律法规和政策，为您提供本协议项下约定的技术服务。</p>
        <p>4. 本平台统计分析方法仅针对数字进行的，如果上传数据中包括非数字信息，可能会被系统直接处理为 NULL 值或者对某些列数据进行删除处理。</p>

        <h2>七、服务的中断和终止</h2>
        <p>1. SPSSGO 会尽全力维护平台的正常运行，以向用户提供持续、稳定、安全、顺畅的服务。但用户理解并同意：SPSSGO 对服务页面进行改版、升级网站系统、增加服务功能等须中断服务的操作时，有权暂时中断服务。SPSSGO 将尽可能在实施以上行为时予以提前公告，并尽可能将影响降低到最小。</p>
        <p>2. 用户可自行停止使用 SPSSGO 提供的服务，并可向 SPSSGO 提交申请，要求注销其帐户。</p>

        <h2>八、责任限制</h2>
        <p>1. 在使用本平台的过程中，可能会遇到不可抗力等风险因素，使系统发生中断。不可抗力是指不能预见、不能克服、不能避免且对一方或双方造成重大影响的客观事件，包括但不限于洪水、地震、瘟疫和风暴等自然灾害以及战争、动乱、政府行为等社会事件。出现上述情况时，本平台将努力在第一时间与相关单位配合及时进行修复。</p>
        <p>2. 在法律允许的范围内，本平台对以下情形导致的服务中断或受阻不承担责任：</p>
        <ul>
          <li>平台系统停机维护或升级；</li>
          <li>因台风、地震、洪水、雷电或恐怖袭击等不可抗力原因；</li>
          <li>您的电脑软硬件和通信线路、供电线路出现故障的；</li>
          <li>因您操作不当或通过非经我们授权或认可的方式使用我们服务的；</li>
          <li>因病毒、木马、恶意程序攻击、网络拥堵、系统不稳定、系统或设备故障、通讯故障、电力故障等原因；</li>
          <li>其他因网络信息或您自身行为引起的风险。</li>
        </ul>

        <h2>九、知识产权</h2>
        <p>1. 本平台上的内容，包括但不限于著作、图片、档案、资讯、资料、网站架构、网站画面的安排、网页设计，均由 SPSSGO 依法拥有知识产权，包括但不限于商标权、专利权、著作权、商业秘密等。</p>
        <p>2. 非经平台书面同意，请勿擅自使用、修改、反向编译、复制、公开传播、改变、散布、发行或公开发表平台系统程序或内容。</p>
        <p>3. 尊重知识产权是您应尽的义务，如有违反，您需要承担损害赔偿责任。</p>

        <h2>十、适用法律及争议解决</h2>
        <p>1. 本协议的订立、执行和解释及争议的解决均应适用中华人民共和国大陆地区法律。</p>
        <p>2. 如发生本协议条款与上述法律相抵触时，则这些条款将完全按上述法律规定重新解释，但不影响其它合法条款对用户产生的法律效力和影响。</p>
        <p>3. 本协议的规定是可分割的，如本协议任何规定被裁定为无效或不可执行，则该规定可被删除，不影响其余条款的继续执行。</p>
        <p>4. 如双方就本协议内容或其执行发生任何争议，双方应尽力友好协商解决；协商不成时，任何一方均可向有管辖权的人民法院提起诉讼。</p>

        <h2>十一、联系我们</h2>
        <p>1. 如您有关于网络信息安全的投诉和举报，或您对本协议、或您的相关事宜有任何问题、意见或建议，请随时与我们联系，可发送电子邮件至 <a href="mailto:jahe@jahe.top">jahe@jahe.top</a>。</p>
        <p>2. 一般情况下，我们将在收到您的问题、意见或建议，并验证您的用户身份后三十天内予以回复。</p>
      </div>

      <!-- 隐私政策 -->
      <div v-if="tab === 'privacy'" class="legal-content">
        <h1>SPSSGO 隐私政策</h1>
        <p class="legal-meta">发布日期：2026.03.31</p>
        <p class="legal-submeta">产品全称：Smart Processing Statistical System Guided Operations</p>
        <p class="legal-owner">运营主体：日照广泰佳和网络科技有限公司</p>

        <p><strong>提示条款：</strong></p>
        <p>您的信任对我们非常重要，我们深知个人信息对您的重要性，我们将按法律法规要求，采取相应安全保护措施，尽力保护您的个人信息安全可控。鉴此，SPSSGO 平台运营方（以下简称"我们"）制定本《隐私政策》（下称"本政策/本隐私政策"）并提醒您：</p>
        <p>本政策适用于 SPSSGO 平台产品或服务。如我们关联公司产品或服务中使用了我们提供的产品或服务但未设独立法律声明及隐私政策的，则本政策同样适用于该部分产品或服务。需要特别说明的是，本政策不适用于其他第三方向您提供的服务。本政策与您使用我们的服务关系紧密，我们建议您仔细阅读并理解本政策全部内容，做出您认为适当的选择。我们努力用通俗易懂、简明扼要的文字表达，并对本政策中与您的权益存在重大关系的条款，采用粗体字进行标注以提示您注意。<strong>您使用或继续使用我们的服务，即意味着同意我们按照本政策收集、使用、储存和分享您的相关信息。</strong>如对本政策或相关事宜有任何问题，请通过 <a href="mailto:jahe@jahe.top">jahe@jahe.top</a> 与我们联系。</p>

        <p>本政策将帮助您了解以下内容：</p>
        <ul>
          <li>我们如何收集和使用您的个人信息</li>
          <li>我们如何使用 Cookie 和同类技术</li>
          <li>我们如何共享、转让、公开披露您的个人信息</li>
          <li>我们如何保护您的个人信息</li>
          <li>您的权利</li>
          <li>我们如何处理未成年人的个人信息</li>
          <li>您的个人信息如何在全球范围转移</li>
          <li>本政策如何更新</li>
          <li>如何联系我们</li>
        </ul>

        <h2>一、我们如何收集和使用您的个人信息</h2>
        <p>（一）为了向所有用户更好的提供产品和/或服务时，我们将遵循正当、合法、必要的原则收集和使用您的个人信息。</p>
        <p>以便我们能够更好为您提供使用产品和/或服务，需要您创建账号，提供用户名和密码。在您主动注销账号时，我们将根据适用法律法规的要求尽快使其匿名或删除您的个人信息。</p>

        <p>（二）为您推荐个性化的信息或服务</p>
        <p>为向您提供个性化的信息或服务，我们可能向您收集和使用您的以下个人信息并进行分析：</p>
        <ul>
          <li>您的浏览记录。</li>
          <li>浏览器自动收集的一些设备信息，包括浏览器类型、IP地址、设备型号、系统版本。</li>
        </ul>
        <p>您可以通过不填写方式来拒绝提供上述信息，不提供上述行为信息的，不影响您正常使用其他功能。</p>

        <p>（三）为向您提供更契合您需求的页面展示、了解产品适配性、识别账号异常状态，我们会收集关于您使用的服务以及使用方式的信息，主要包括：</p>
        <ul>
          <li>设备信息：我们会根据您在软件安装及使用中授权的具体权限，接收并记录您所使用的设备相关信息（例如设备型号、操作系统版本、设备设置等软硬件特征信息）。</li>
          <li>日志信息：当您使用我们的产品或服务时，我们会自动收集您对我们服务的详细使用情况，作为有关网络日志保存。</li>
        </ul>
        <p>请注意，单独的设备信息、日志信息等是无法识别特定自然人身份的信息。如果我们将这类非个人信息与其他信息结合用于识别特定自然人身份，或者将其与个人信息结合使用，则在结合使用期间，这类非个人信息将被视为个人信息，除取得您授权或法律法规另有规定外，我们会将该类个人信息做匿名化、去标识化处理。</p>

        <p>（四）征得授权同意的例外</p>
        <p>根据相关法律法规规定，以下情形中收集您的个人信息无需征得您的授权同意：</p>
        <ul>
          <li>与国家安全、国防安全有关的；</li>
          <li>与公共安全、公共卫生、重大公共利益有关的；</li>
          <li>与犯罪侦查、起诉、审判和判决执行等有关的；</li>
          <li>出于维护个人信息主体或其他个人的生命、财产等重大合法权益但又很难得到您本人同意的；</li>
          <li>所收集的个人信息是您自行向社会公众公开的；</li>
          <li>从合法公开披露的信息中收集个人信息的，如合法的新闻报道、政府信息公开等渠道；</li>
          <li>根据您的要求签订合同所必需的；</li>
          <li>用于维护所提供的产品或服务的安全稳定运行所必需的，例如发现、处置产品或服务的故障；</li>
          <li>法律法规规定的其他情形。</li>
        </ul>
        <p>如我们停止运营平台产品或服务，我们将及时停止继续收集您个人信息的活动，将停止运营的通知以公告的形式通知您，对所持有的个人信息进行删除或匿名化处理。</p>

        <h2>二、我们如何使用 Cookie 和同类技术</h2>
        <p>为确保网站正常运转，我们有时会在计算机或移动设备上存储名为 Cookie 的小数据文件。Cookie 是一种网络服务器存储在计算机或移动设备上的纯文本文件。Cookie 的内容只能由创建它的服务器检索或读取。每个 Cookie 对您的网络浏览器或移动应用程序都是唯一的。Cookie 通常包含标识符、站点名称以及一些号码和字符。借助于 Cookie，网站能够存储用户偏好等数据。</p>
        <p>我们启用 Cookie 的目的与大多数网站或互联网服务提供商启用 Cookie 的目的一样，即改善用户体验。借助于 Cookie，网站能够记住用户的单次访问（使用会话 Cookie）或多次访问（使用永久 Cookie）。借助于 Cookie，网站能够保存设置，例如计算机或移动设备的语言、字体大小和其他浏览偏好。这意味着，用户无需在每次访问时重新配置用户偏好设置。</p>
        <p>我们不会将 Cookie 用于本政策所述目的之外的任何用途。您可根据自己的偏好管理或删除 Cookie。您可以清除计算机上保存的所有 Cookie，大部分网络浏览器都设有阻止 Cookie 的功能。但如果您这么做，则需要在每一次访问我们的网站时亲自更改用户设置。</p>

        <h2>三、我们如何共享、转让、公开披露您的个人信息</h2>
        <p><strong>（一）共享</strong></p>
        <p>我们不会与本平台服务提供者以外的公司、组织和个人共享您的个人信息，但以下情况除外：</p>
        <ul>
          <li>在获取明确同意的情况下共享：获得您的明确同意后，我们会与其他方共享您的个人信息。</li>
          <li>在法定情形下的共享：我们可能会根据法律法规规定、诉讼争议解决需要，或按行政、司法机关依法提出的要求，对外共享您的个人信息。</li>
          <li>在您主动选择情况下共享：若您主动选择共享后，我们会与其他方共享您的个人信息。</li>
          <li>与授权合作伙伴共享：我们可能委托授权合作伙伴为您提供某些服务或代表我们履行职能。我们仅会出于合法、正当、必要、特定、明确的目的共享您的信息，授权合作伙伴只能接触到其履行职责所需信息，且不能将此信息用于其他任何目的。</li>
        </ul>
        <p><strong>（二）转让</strong></p>
        <p>我们不会将您的个人信息转让给任何公司、组织和个人，但以下情况除外：</p>
        <ul>
          <li>在获取明确同意的情况下转让：获得您的明确同意后，我们会向其他方转让您的个人信息；</li>
          <li>在本平台发生合并、收购或破产清算情形时，如涉及到个人信息转让，我们会要求新的持有您个人信息的公司、组织继续受本政策的约束，否则我们将要求该公司、组织和个人重新向您征求授权同意。</li>
        </ul>
        <p><strong>（三）公开披露</strong></p>
        <p>我们仅会在以下情况下，公开披露您的个人信息：</p>
        <ul>
          <li>获得您明确同意或基于您的主动选择，我们可能会公开披露您的个人信息；</li>
          <li>基于法律的披露：在法律、法律程序、诉讼或政府主管部门强制性要求的情况下，我们可能会公开披露您的个人信息。</li>
        </ul>

        <h2>四、我们如何保护您的个人信息</h2>
        <p>（一）我们已采取符合业界标准、合理可行的安全防护措施保护您提供的个人信息安全，防止个人信息遭到未经授权访问、公开披露、使用、修改、损坏或丢失。我们会使用加密技术提高个人信息的安全性；我们会使用受信赖的保护机制防止个人信息遭到恶意攻击；我们会部署访问控制机制，尽力确保只有授权人员才可访问个人信息。</p>
        <p>（二）我们只会在达成本政策所述目的所需的期限内保留您的个人信息，除非延长保留期征得您的同意或法律有强制的存留要求。</p>
        <p>（三）请您妥善保护自己的个人信息，仅在必要的情形下向他人提供。如您发现自己的个人信息尤其是您的账户或密码发生泄露，请您立即联络我们，以便我们根据您的申请采取相应措施。</p>
        <p>（四）在不幸发生个人信息安全事件后，我们将按照法律法规的要求向您告知：安全事件的基本情况和可能的影响、我们已采取或将要采取的处置措施、您可自主防范和降低风险的建议、对您的补救措施等。事件相关情况我们将以邮件、信函、电话、推送通知等方式告知您，难以逐一告知个人信息主体时，我们会采取合理、有效的方式发布公告。</p>

        <h2>五、您的权利</h2>
        <p>我们将尽一切可能采取适当的技术手段，保证您可以访问、更新和更正自己的注册信息或使用我们的服务时提供的其他个人信息。您有权利查询、更正、管理、删除自己的信息并保护自己的隐私和安全。</p>
        <ul>
          <li><strong>访问您的个人信息</strong>：除法律法规规定的例外情况，无论您何时使用我们的服务，我们都会力求让您顺利访问自己的个人信息。您可以在产品中访问或编辑您的帐户中的个人资料信息。</li>
          <li><strong>更正或补充您的个人信息</strong>：当您需要更新您的个人信息时，或发现我们处理您的个人信息有错误时，您有权作出更正或更新。</li>
          <li><strong>删除您的个人信息</strong>：如我们处理个人信息的行为违反法律法规，或未征得您的同意，您可以向我们提出删除请求。</li>
          <li><strong>注销账户</strong>：在您主动注销账户之后，我们将停止为您提供产品或服务，根据适用法律的要求删除您的个人信息，或使其匿名化处理。</li>
          <li><strong>响应您的请求</strong>：为保障安全，您可能需要提供书面请求，或以其他方式证明您的身份。我们将在 15 天内做出答复。</li>
        </ul>

        <h2>六、我们如何处理未成年人的个人信息</h2>
        <p>如您为未成年人的，我们建议您请您的父母或监护人仔细阅读本隐私政策，并在征得您的父母或监护人同意的前提下使用我们的服务或向我们提供信息。</p>
        <p>对于经父母或监护人同意使用我们的产品或服务而收集未成年人个人信息的情况，我们只会在法律法规允许、父母或监护人明确同意或者保护未成年人所必要的情况下使用、共享、转让或披露此信息。</p>

        <h2>七、您的个人信息如何在全球范围转移</h2>
        <p>我们在中华人民共和国境内运营中收集和产生的个人信息，存储在中国境内，以下情形除外：</p>
        <ul>
          <li>法律法规有明确规定；</li>
          <li>获得您的明确授权；</li>
          <li>您通过互联网进行跨境数据传播等个人主动行为。</li>
        </ul>
        <p>针对以上情形，我们会确保依据本隐私政策对您的个人信息提供足够的保护。</p>

        <h2>八、本隐私政策如何更新</h2>
        <p>我们的隐私政策可能变更。未经您明确同意，我们不会限制您按照本隐私政策所应享有的权利。我们会在专门页面上展示最新版的隐私政策。</p>
        <p>对于重大变更，我们还会提供更为显著的通知（包括我们会通过平台公示的方式进行通知甚至向您提供弹窗提示）。</p>
        <p>本政策所指的重大变更包括但不限于：</p>
        <ul>
          <li>我们的服务模式发生重大变化，如处理个人信息的目的、处理的个人信息类型、个人信息的使用方式等；</li>
          <li>我们在控制权等方面发生重大变化，如并购重组等引起的所有者变更等；</li>
          <li>个人信息共享、转让或公开披露的主要对象发生变化；</li>
          <li>您参与个人信息处理方面的权利及其行使方式发生重大变化；</li>
          <li>我们负责处理个人信息安全的责任部门、联络方式及投诉渠道发生变化时；</li>
          <li>个人信息安全影响评估报告表明存在高风险时。</li>
        </ul>

        <h2>九、如何联系我们</h2>
        <p>您可以通过以下方式与我们联系，我们将在 15 天内回复您的请求：</p>
        <p>1. 如对本政策内容有任何疑问、意见或建议，您可发送电子邮件至 <a href="mailto:jahe@jahe.top">jahe@jahe.top</a> 与我们联系；</p>
        <p>2. 如发现个人信息可能被泄露，您可通过上述邮箱向我们投诉举报。</p>
        <p>如果您对我们的回复不满意，特别是您认为我们的个人信息处理行为损害了您的合法权益，您还可以通过向有管辖权的人民法院提起诉讼来寻求解决方案。</p>
      </div>

      <!-- 开源协议 -->
      <div v-if="tab === 'license'" class="legal-content">
        <h1>开源协议 (AGPL-3.0)</h1>
        <p class="legal-meta">发布日期：2026.03.31</p>
        <p class="legal-submeta">产品全称：Smart Processing Statistical System Guided Operations</p>
        <p class="legal-owner">版权归属：日照广泰佳和网络科技有限公司</p>

        <div class="license-lang-toggle">
          <button :class="{ active: licenseLang === 'zh' }" @click="licenseLang = 'zh'">中文说明</button>
          <button :class="{ active: licenseLang === 'en' }" @click="licenseLang = 'en'">English Original</button>
        </div>

        <!-- 英文原版 -->
        <div v-if="licenseLang === 'en'" class="license-en-text">
          <div class="license-en-notice">
            <p>SPSSGO 3.0 Community Edition is released under the GNU Affero General Public License v3.0 (AGPL-3.0).</p>
            <p>Copyright holder: <strong>Rizhao Guangtai Jiahe Network Technology Co., Ltd.</strong></p>
          </div>
          <pre class="license-pre">                    GNU AFFERO GENERAL PUBLIC LICENSE
                       Version 3, 19 November 2007

 Copyright (C) 2007 Free Software Foundation, Inc. &lt;http://fsf.org/&gt;
 Everyone is permitted to copy and distribute verbatim copies
 of this license document, but changing it is not allowed.

                            Preamble

  The GNU Affero General Public License is a free, copyleft license for
software and other kinds of works, specifically designed to ensure
cooperation with the community in the case of network server software.

  The licenses for most software and other practical works are designed
to take away your freedom to share and change the works.  By contrast,
our General Public Licenses are intended to guarantee your freedom to
share and change all versions of a program--to make sure it remains free
software for all its users.

  When we speak of free software, we are referring to freedom, not
price.  Our General Public Licenses are designed to make sure that you
have the freedom to distribute copies of free software (and charge for
them if you wish), that you receive source code or can get it if you
want it, that you can change the software or use pieces of it in new
free programs, and that you know you can do these things.

  Developers that use our General Public Licenses protect your rights
with two steps: (1) assert copyright on the software, and (2) offer
you this License which gives you legal permission to copy, distribute
and/or modify the software.

  A secondary benefit of defending all users' freedom is that
improvements made in alternate versions of the program, if they
receive widespread use, become available for other developers to
incorporate.  Many developers of free software are heartened and
encouraged by the resulting cooperation.  However, in the case of
software used on network servers, this result may fail to come about.
The GNU General Public License permits making a modified version and
letting the public access it on a server without ever releasing its
source code to the public.

  The GNU Affero General Public License is designed specifically to
ensure that, in such cases, the modified source code becomes available
to the community.  It requires the operator of a network server to
provide the source code of the modified version running there to the
users of that server.  Therefore, public use of a modified version, on
a publicly accessible server, gives the public access to the source
code of the modified version.

  An older license, called the Affero General Public License and
published by Affero, was designed to accomplish similar goals.  This is
a different license, not a version of the Affero GPL, but Affero has
released a new version of the Affero GPL which permits relicensing under
this license.

  The precise terms and conditions for copying, distribution and
modification follow.

                       TERMS AND CONDITIONS

  0. Definitions.

  "This License" refers to version 3 of the GNU Affero General Public License.

  "Copyright" also means copyright-like laws that apply to other kinds of
works, such as semiconductor masks.

  "The Program" refers to any copyrightable work licensed under this
License.  Each licensee is addressed as "you".  "Licensees" and
"recipients" may be individuals or organizations.

  To "modify" a work means to copy from or adapt all or part of the work
in a fashion requiring copyright permission, other than the making of an
exact copy.  The resulting work is called a "modified version" of the
earlier work or a work "based on" the earlier work.

  A "covered work" means either the unmodified Program or a work based
on the Program.

  To "propagate" a work means to do anything with it that, without
permission, would make you directly or secondarily liable for
infringement under applicable copyright law, except executing it on a
computer or modifying a private copy.  Propagation includes copying,
distribution (with or without modification), making available to the
public, and in some countries other activities as well.

  To "convey" a work means any kind of propagation that enables other
parties to make or receive copies.  Mere interaction with a user through
a computer network, with no transfer of a copy, is not conveying.

  An interactive user interface displays "Appropriate Legal Notices"
to the extent that it includes a convenient and prominently visible
feature that (1) displays an appropriate copyright notice, and (2)
tells the user that there is no warranty for the work (except to the
extent that warranties are provided), that licensees may convey the
work under this License, and how to view a copy of this License.  If
the interface presents a list of user commands or options, such as a
menu, a prominent item in the list meets this criterion.

  1. Source Code.

  The "source code" for a work means the preferred form of the work
for making modifications to it.  "Object code" means any non-source
form of a work.

  A "Standard Interface" means an interface that either is an official
standard defined by a recognized standards body, or, in the case of
interfaces specified for a particular programming language, one that
is widely used among developers working in that language.

  The "System Libraries" of an executable work include anything, other
than the work as a whole, that (a) is included in the normal form of
packaging a Major Component, but which is not part of that Major
Component, and (b) serves only to enable use of the work with that
Major Component, or to implement a Standard Interface for which an
implementation is available to the public in source code form.  A
"Major Component", in this context, means a major essential component
(kernel, window system, and so on) of the specific operating system
(if any) on which the executable work runs, or a compiler used to
produce the work, or an object code interpreter used to run it.

  The "Corresponding Source" for a work in object code form means all
the source code needed to generate, install, and (for an executable
work) run the object code and to modify the work, including scripts to
control those activities.  However, it does not include the work's
System Libraries, or general-purpose tools or generally available free
programs which are used unmodified in performing those activities but
which are not part of the work.  For example, Corresponding Source
includes interface definition files associated with source files for
the work, and the source code for shared libraries and dynamically
linked subprograms that the work is specifically designed to require,
such as by intimate data communication or control flow between those
subprograms and other parts of the work.

  The Corresponding Source need not include anything that users
can regenerate automatically from other parts of the Corresponding
Source.

  The Corresponding Source for a work in source code form is that
same work.

  2. Basic Permissions.

  All rights granted under this License are granted for the term of
copyright on the Program, and are irrevocable provided the stated
conditions are met.  This License explicitly affirms your unlimited
permission to run the unmodified Program.  The output from running a
covered work is covered by this License only if the output, given its
content, constitutes a covered work.  This License acknowledges your
rights of fair use or other equivalent, as provided by copyright law.

  You may make, run and propagate covered works that you do not
convey, without conditions so long as your license otherwise remains
in force.  You may convey covered works to others for the sole purpose
of having them make modifications exclusively for you, or provide you
with facilities for running those works, provided that you comply with
the terms of this License in conveying all material for which you do
not control copyright.  Those thus making or running the covered works
for you must do so exclusively on your behalf, under your direction
and control, on terms that prohibit them from making any copies of
your copyrighted material outside their relationship with you.

  Conveying under any other circumstances is permitted solely under
the conditions stated below.  Sublicensing is not allowed; section 10
makes it unnecessary.

  3. Protecting Users' Legal Rights From Anti-Circumvention Law.

  No covered work shall be deemed part of an effective technological
measure under any applicable law fulfilling obligations under article
11 of the WIPO copyright treaty adopted on 20 December 1996, or
similar laws prohibiting or restricting circumvention of such
measures.

  When you convey a covered work, you waive any legal power to forbid
circumvention of technological measures to the extent such circumvention
is effected by exercising rights under this License with respect to
the covered work, and you disclaim any intention to limit operation or
modification of the work as a means of enforcing, against the work's
users, your or third parties' legal rights to forbid circumvention of
technological measures.

  4. Conveying Verbatim Copies.

  You may convey verbatim copies of the Program's source code as you
receive it, in any medium, provided that you conspicuously and
appropriately publish on each copy an appropriate copyright notice;
keep intact all notices stating that this License and any
non-permissive terms added in accord with section 7 apply to the code;
keep intact all notices of the absence of any warranty; and give all
recipients a copy of this License along with the Program.

  You may charge any price or no price for each copy that you convey,
and you may offer support or warranty protection for a fee.

  5. Conveying Modified Source Versions.

  You may convey a work based on the Program, or the modifications to
produce it from the Program, in the form of source code under the
terms of section 4, provided that you also meet all of these conditions:

    a) The work must carry prominent notices stating that you modified
    it, and giving a relevant date.

    b) The work must carry prominent notices stating that it is
    released under this License and any conditions added under section
    7.  This requirement modifies the requirement in section 4 to
    "keep intact all notices".

    c) You must license the entire work, as a whole, under this
    License to anyone who comes into possession of a copy.  This
    License will therefore apply, along with any applicable section 7
    additional terms, to the whole of the work, and all its parts,
    regardless of how they are packaged.  This License gives no
    permission to license the work in any other way, but it does not
    invalidate such permission if you have separately received it.

    d) If the work has interactive user interfaces, each must display
    Appropriate Legal Notices; however, if the Program has interactive
    interfaces that do not display Appropriate Legal Notices, your
    work need not make them do so.

  A compilation of a covered work with other separate and independent
works, which are not by their nature extensions of the covered work,
and which are not combined with it such as to form a larger program,
in or on a volume of a storage or distribution medium, is called an
"aggregate" if the compilation and its resulting copyright are not
used to limit the access or legal rights of the compilation's users
beyond what the individual works permit.  Inclusion of a covered work
in an aggregate does not cause this License to apply to the other
parts of the aggregate.

  6. Conveying Non-Source Forms.

  You may convey a covered work in object code form under the terms
of sections 4 and 5, provided that you also convey the
machine-readable Corresponding Source under the terms of this License,
in one of these ways:

    a) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by the
    Corresponding Source fixed on a durable physical medium
    customarily used for software interchange.

    b) Convey the object code in, or embodied in, a physical product
    (including a physical distribution medium), accompanied by a
    written offer, valid for at least three years and valid for as
    long as you offer spare parts or customer support for that product
    model, to give anyone who possesses the object code either (1) a
    copy of the Corresponding Source for all the software in the
    product that is covered by this License, on a durable physical
    medium customarily used for software interchange, for a price no
    more than your reasonable cost of physically performing this
    conveying of source, or (2) access to copy the
    Corresponding Source from a network server at no charge.

    c) Convey individual copies of the object code with a copy of the
    written offer to provide the Corresponding Source.  This
    alternative is allowed only occasionally and noncommercially, and
    only if you received the object code with such an offer, in accord
    with subsection 6b.

    d) Convey the object code by offering access from a designated
    place (gratis or for a charge), and offer equivalent access to the
    Corresponding Source in the same way through the same place at no
    further charge.  You need not require recipients to copy the
    Corresponding Source along with the object code.  If the place to
    copy the object code is a network server, the Corresponding Source
    may be on a different server (operated by you or a third party)
    that supports equivalent copying facilities, provided you maintain
    clear directions next to the object code saying where to find the
    Corresponding Source.  Regardless of what server hosts the
    Corresponding Source, you remain obligated to ensure that it is
    available for as long as needed to satisfy these requirements.

    e) Convey the object code using peer-to-peer transmission, provided
    you inform other peers where the object code and Corresponding
    Source of the work are being offered to the general public at no
    charge under subsection 6d.

  A separable portion of the object code, whose source code is excluded
from the Corresponding Source as a System Library, need not be
included in conveying the object code work.

  A "User Product" is either (1) a "consumer product", which means any
tangible personal property which is normally used for personal, family,
or household purposes, or (2) anything designed or sold for incorporation
into a dwelling.  In determining whether a product is a consumer product,
doubtful cases shall be resolved in favor of coverage.  For a particular
product received by a particular user, "normally used" refers to a
typical or common use of that class of product, regardless of the status
of the particular user or of the way in which the particular user
actually uses, or expects or is expected to use, the product.  A product
is a consumer product regardless of whether the product has substantial
commercial, industrial or non-consumer uses, unless such uses represent
the only significant mode of use of the product.

  "Installation Information" for a User Product means any methods,
procedures, authorization keys, or other information required to install
and execute modified versions of a covered work in that User Product from
a modified version of its Corresponding Source.  The information must
suffice to ensure that the continued functioning of the modified object
code is in no case prevented or interfered with solely because
modification has been made.

  If you convey an object code work under this section in, or with, or
specifically for use in, a User Product, and the conveying occurs as
part of a transaction in which the right of possession and use of the
User Product is transferred to the recipient in perpetuity or for a
fixed term (regardless of how the transaction is characterized), the
Corresponding Source conveyed under this section must be accompanied
by the Installation Information.  But this requirement does not apply
if neither you nor any third party retains the ability to install
modified object code on the User Product (for example, the work has
been installed in ROM).

  The requirement to provide Installation Information does not include a
requirement to continue to provide support service, warranty, or updates
for a work that has been modified or installed by the recipient, or for
the User Product in which it has been modified or installed.  Access to a
network may be denied when the modification itself materially and
adversely affects the operation of the network or violates the rules and
protocols for communication across the network.

  Corresponding Source conveyed, and Installation Information provided,
in accord with this section must be in a format that is publicly
documented (and with an implementation available to the public in
source code form), and must require no special password or key for
unpacking, reading or copying.

  7. Additional Terms.

  "Additional permissions" are terms that supplement the terms of this
License by making exceptions from one or more of its conditions.
Additional permissions that are applicable to the entire Program shall
be treated as though they were included in this License, to the extent
that they are valid under applicable law.  If additional permissions
apply only to part of the Program, that part may be used separately
under those permissions, but the entire Program remains governed by
this License without regard to the additional permissions.

  When you convey a copy of a covered work, you may at your option
remove any additional permissions from that copy, or from any part of
it.  (Additional permissions may be written to require their own
removal in certain cases when you modify the work.)  You may place
additional permissions on material, added by you to a covered work,
for which you have or can give appropriate copyright permission.

  Notwithstanding any other provision of this License, for material you
add to a covered work, you may (if authorized by the copyright holders of
that material) supplement the terms of this License with terms:

    a) Disclaiming warranty or limiting liability differently from the
    terms of sections 15 and 16 of this License; or

    b) Requiring preservation of specified reasonable legal notices or
    author attributions in that material or in the Appropriate Legal
    Notices displayed by works containing it; or

    c) Prohibiting misrepresentation of the origin of that material, or
    requiring that modified versions of such material be marked in
    reasonable ways as different from the original version; or

    d) Limiting the use for publicity purposes of names of licensors or
    authors of the material; or

    e) Declining to grant rights under trademark law for use of some
    trade names, trademarks, or service marks; or

    f) Requiring indemnification of licensors and authors of that
    material by anyone who conveys the material (or modified versions of
    it) with contractual assumptions of liability to the recipient, for
    any liability that these contractual assumptions directly impose on
    those licensors and authors.

  All other non-permissive additional terms are considered "further
restrictions" within the meaning of section 10.  If the Program as you
received it, or any part of it, contains a notice stating that it is
governed by this License along with a term that is a further
restriction, you may remove that term.  If a license document contains
a further restriction but permits relicensing or conveying under this
License, you may add to a covered work material governed by the terms
of that license document, provided that the further restriction does
not survive such relicensing or conveying.

  If you add terms to a covered work in accord with this section, you
must place, in the relevant source files, a statement of the
additional terms that apply to those files, or a notice indicating
where to find the applicable terms.

  Additional terms, permissive or non-permissive, may be stated in the
form of a separately written license, or stated as exceptions;
the above requirements apply either way.

  8. Termination.

  You may not propagate or modify a covered work except as expressly
provided under this License.  Any attempt otherwise to propagate or
modify it is void, and will automatically terminate your rights under
this License (including any patent licenses granted under the third
paragraph of section 11).

  However, if you cease all violation of this License, then your
license from a particular copyright holder is reinstated (a)
provisionally, unless and until the copyright holder explicitly and
finally terminates your license, and (b) permanently, if the copyright
holder fails to notify you of the violation by some reasonable means
prior to 60 days after the cessation.

  Moreover, your license from a particular copyright holder is
reinstated permanently if the copyright holder notifies you of the
violation by some reasonable means, this is the first time you have
received notice of violation of this License (for any work) from that
copyright holder, and you cure the violation prior to 30 days after
your receipt of the notice.

  Termination of your rights under this section does not terminate the
licenses of parties who have received copies or rights from you under
this License.  If your rights have been terminated and not permanently
reinstated, you do not qualify to receive new licenses for the same
material under section 10.

  9. Acceptance Not Required for Having Copies.

  You are not required to accept this License in order to receive or
run a copy of the Program.  Ancillary propagation of a covered work
occurring solely as a consequence of using peer-to-peer transmission
to receive a copy likewise does not require acceptance.  However,
nothing other than this License grants you permission to propagate or
modify any covered work.  These actions infringe copyright if you do
not accept this License.  Therefore, by modifying or propagating a
covered work, you indicate your acceptance of this License to do so.

  10. Automatic Licensing of Downstream Recipients.

  Each time you convey a covered work, the recipient automatically
receives a license from the original licensors, to run, modify and
propagate that work, subject to this License.  You are not responsible
for enforcing compliance by third parties with this License.

  An "entity transaction" is a transaction transferring control of an
organization, or substantially all assets of one, or subdividing an
organization, or merging organizations.  If propagation of a covered
work results from an entity transaction, each party to that
transaction who receives a copy of the work also receives whatever
licenses to the work the party's predecessor in interest had or could
give under the previous paragraph, plus a right to possession of the
Corresponding Source of the work from the predecessor in interest, if
the predecessor has it or can get it with reasonable efforts.

  You may not impose any further restrictions on the exercise of the
rights granted or affirmed under this License.  For example, you may
not impose a license fee, royalty, or other charge for exercise of
rights granted under this License, and you may not initiate litigation
(including a cross-claim or counterclaim in a lawsuit) alleging that
any patent claim is infringed by making, using, selling, offering for
sale, or importing the Program or any portion of it.

  11. Patents.

  A "contributor" is a copyright holder who authorizes use under this
License of the Program or a work on which the Program is based.  The
work thus licensed is called the contributor's "contributor version".

  A contributor's "essential patent claims" are all patent claims
owned or controlled by the contributor, whether already acquired or
hereafter acquired, that would be infringed by some manner, permitted
by this License, of making, using, or selling its contributor version,
but do not include claims that would be infringed only as a
consequence of further modification of the contributor version.  For
purposes of this definition, "control" includes the right to grant
patent sublicenses in a manner consistent with the requirements of
this License.

  Each contributor grants you a non-exclusive, worldwide, royalty-free
patent license under the contributor's essential patent claims, to
make, use, sell, offer for sale, import and otherwise run, modify and
propagate the contents of its contributor version.

  In the following three paragraphs, a "patent license" is any express
agreement or commitment, however denominated, not to enforce a patent
(such as an express permission to practice a patent or covenant not to
sue for patent infringement).  To "grant" such a patent license to a
party means to make such an agreement or commitment not to enforce a
patent against the party.

  If you convey a covered work, knowingly relying on a patent license,
and the Corresponding Source of the work is not available for anyone
to copy, free of charge and under the terms of this License, through a
publicly available network server or other readily accessible means,
then you must either (1) cause the Corresponding Source to be so
available, or (2) arrange to deprive yourself of the benefit of the
patent license for this particular work, or (3) arrange, in a manner
consistent with the requirements of this License, to extend the patent
license to downstream recipients.  "Knowingly relying" means you have
actual knowledge that, but for the patent license, your conveying the
covered work in a country, or your recipient's use of the covered work
in a country, would infringe one or more identifiable patents in that
country that you have reason to believe are valid.

  If, pursuant to or in connection with a single transaction or
arrangement, you convey, or propagate by procuring conveyance of, a
covered work, and grant a patent license to some of the parties
receiving the covered work authorizing them to use, propagate, modify
or convey a specific copy of the covered work, then the patent license
you grant is automatically extended to all recipients of the covered
work and works based on it.

  A patent license is "discriminatory" if it does not include within
the scope of its coverage, prohibits the exercise of, or is
conditioned on the non-exercise of one or more of the rights that are
specifically granted under this License.  You may not convey a covered
work if you are a party to an arrangement with a third party that is
in the business of distributing software, under which you make payment
to the third party based on the extent of your activity of conveying
the work, and under which the third party grants, to any of the
parties who would receive the covered work from you, a discriminatory
patent license (a) in connection with copies of the covered work
conveyed by you (or copies made from those copies), or (b) primarily
for and in connection with specific products or compilations that
contain the covered work, unless you entered into that arrangement,
or that patent license was granted, prior to 28 March 2007.

  Nothing in this License shall be construed as excluding or limiting
any implied license or other defenses to infringement that may
otherwise be available to you under applicable patent law.

  12. No Surrender of Others' Freedom.

  If conditions are imposed on you (whether by court order, agreement or
otherwise) that contradict the conditions of this License, they do not
excuse you from the conditions of this License.  If you cannot convey a
covered work so as to satisfy simultaneously your obligations under this
License and any other pertinent obligations, then as a consequence you may
not convey it at all.  For example, if you agree to terms that obligate you
to collect a royalty for further conveying from those to whom you convey
the Program, the only way you could satisfy both those terms and this
License would be to refrain entirely from conveying the Program.

  13. Remote Network Interaction; Use with the GNU General Public License.

  Notwithstanding any other provision of this License, if you modify the
Program, your modified version must prominently offer all users
interacting with it remotely through a computer network (if your version
supports such interaction) an opportunity to receive the Corresponding
Source of your version by providing access to the Corresponding Source
from a network server at no charge, through some standard or customary
means of facilitating copying of software.  This Corresponding Source
shall include the Corresponding Source for any work covered by version 3
of the GNU General Public License that is incorporated pursuant to the
following paragraph.

  Notwithstanding any other provision of this License, you have
permission to link or combine any covered work with a work licensed
under version 3 of the GNU General Public License into a single
combined work, and to convey the resulting work.  The terms of this
License will continue to apply to the part which is the covered work,
but the work with which it is combined will remain governed by version
3 of the GNU General Public License.

  14. Revised Versions of this License.

  The Free Software Foundation may publish revised and/or new versions of
the GNU Affero General Public License from time to time.  Such new versions
will be similar in spirit to the present version, but may differ in detail to
address new problems or concerns.

  Each version is given a distinguishing version number.  If the
Program specifies that a certain numbered version of the GNU Affero General
Public License "or any later version" applies to it, you have the
option of following the terms and conditions either of that numbered
version or of any later version published by the Free Software
Foundation.  If the Program does not specify a version number of the
GNU Affero General Public License, you may choose any version ever published
by the Free Software Foundation.

  If the Program specifies that a proxy can decide which future
versions of the GNU Affero General Public License can be used, that proxy's
public statement of acceptance of a version permanently authorizes you
to choose that version for the Program.

  Later license versions may give you additional or different
permissions.  However, no additional obligations are imposed on any
author or copyright holder as a result of your choosing to follow a
later version.

  15. Disclaimer of Warranty.

  THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
ALL NECESSARY SERVICING, REPAIR OR CORRECTION.

  16. Limitation of Liability.

  IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW OR AGREED TO IN WRITING
WILL ANY COPYRIGHT HOLDER, OR ANY OTHER PARTY WHO MODIFIES AND/OR CONVEYS
THE PROGRAM AS PERMITTED ABOVE, BE LIABLE TO YOU FOR DAMAGES, INCLUDING ANY
GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE
USE OR INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF
DATA OR DATA BEING RENDERED INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD
PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE WITH ANY OTHER PROGRAMS),
EVEN IF SUCH HOLDER OR OTHER PARTY HAS BEEN ADVISED OF THE POSSIBILITY OF
SUCH DAMAGES.

  17. Interpretation of Sections 15 and 16.

  If the disclaimer of warranty and limitation of liability provided
above cannot be given local legal effect according to their terms,
reviewing courts shall apply local law that most closely approximates
an absolute waiver of all civil liability in connection with the
Program, unless a warranty or assumption of liability accompanies a
copy of the Program in return for a fee.

                     END OF TERMS AND CONDITIONS</pre>
        </div>

        <!-- 中文说明 -->
        <template v-else>

        <p>SPSSGO 3.0 数据分析工作台 社区版 基于 <strong>GNU Affero General Public License v3.0（AGPL-3.0）</strong> 开源协议发布。</p>

        <h2>一、协议概述</h2>
        <p>AGPL-3.0 是一种强 Copyleft 自由软件许可证，由自由软件基金会（FSF）发布。它要求任何修改或衍生作品也必须在相同的许可下发布，并且通过网络提供服务时也需要公开源代码。</p>

        <h2>二、您可以做什么</h2>
        <ul>
          <li><strong>个人学习与研究</strong> — 您可以自由地下载、安装和使用本软件进行个人学习和学术研究，无需支付任何费用。</li>
          <li><strong>查看和修改源代码</strong> — 您可以自由查看、修改本软件的源代码。</li>
          <li><strong>再分发</strong> — 您可以将本软件及其修改版本分发给他人，但必须同样以 AGPL-3.0 协议发布，并保留原始版权声明。</li>
        </ul>

        <h2>三、您需要遵守的规则</h2>
        <ul>
          <li><strong>保留版权声明</strong> — 您在使用、修改或分发本软件时，必须保留原始版权声明和许可证信息。</li>
          <li><strong>相同协议分发</strong> — 如果您修改了本软件，修改后的版本必须同样以 AGPL-3.0 协议发布。</li>
          <li><strong>网络服务公开源代码</strong> — 如果您通过网络向用户提供基于本软件的服务，您必须向用户提供获取完整源代码的途径。</li>
          <li><strong>声明修改内容</strong> — 您需要在修改的文件中注明修改内容和日期。</li>
        </ul>

        <h2>四、商业使用说明</h2>
        <p>AGPL-3.0 允许商业使用，但需遵守以下条件：</p>
        <ul>
          <li><strong>商业部署</strong> — 如果您将本软件用于商业用途（包括但不限于企业内部使用、对外提供 SaaS 服务），需遵守 AGPL-3.0 协议的全部条款，包括公开源代码。</li>
          <li><strong>闭源商业授权</strong> — 如果您希望以闭源方式进行商业使用（不公开源代码），请联系作者获取商业授权许可。</li>
          <li><strong>企业内部部署</strong> — 企业内部部署并通过网络提供服务的，同样需要遵守 AGPL-3.0 的源代码公开要求，或联系作者获取企业授权。</li>
          <li><strong>教育机构</strong> — 学校及教育机构如需部署使用，请联系作者获取教育授权。</li>
        </ul>

        <h2>五、免责声明</h2>
        <p>本软件按"原样"提供，不附带任何明示或暗示的担保，包括但不限于对适销性、特定用途的适用性和非侵权的担保。在任何情况下，作者或版权持有人均不对因软件或软件的使用或其他交易而产生的任何索赔、损害或其他责任承担责任。</p>

        <h2>六、版权归属</h2>
        <p>本软件版权归属 <strong>日照广泰佳和网络科技有限公司</strong> 所有。</p>

        <h2>七、联系方式</h2>
        <p>如需商业授权、企业授权或教育授权，请通过以下方式联系：</p>
        <ul>
          <li>公司邮箱：<a href="mailto:jahe@jahe.top">jahe@jahe.top</a></li>
          <li>开发者QQ群：978402915</li>
          <li>作者QQ：986968597</li>
          <li>作者邮箱：<a href="mailto:986968597@qq.com">986968597@qq.com</a></li>
        </ul>

        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const tab = ref('terms')
const licenseLang = ref('zh')

onMounted(() => {
  const hash = window.location.hash.replace('#', '')
  if (hash === 'privacy') tab.value = 'privacy'
  if (hash === 'license') tab.value = 'license'
})
</script>

<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: -apple-system, "Segoe UI", "Microsoft YaHei", sans-serif;
  color: #1f2937; background: #f8f9fb;
  -webkit-font-smoothing: antialiased;
}
.legal-page { min-height: 100vh; }

.legal-nav {
  position: sticky; top: 0; z-index: 10;
  background: #fff; border-bottom: 1px solid #eee;
  display: flex; align-items: center; justify-content: space-between;
  padding: 0 32px; height: 56px;
}
.legal-nav-logo img { height: 26px; width: auto; }
.legal-back {
  font-size: 13px; color: #6b7280; text-decoration: none; transition: color .2s;
}
.legal-back:hover { color: #1f2937; }

.legal-container {
  max-width: 800px; margin: 0 auto; padding: 32px 24px 80px;
}

.legal-tabs {
  display: flex; gap: 4px; margin-bottom: 32px;
  background: #eef0f4; border-radius: 10px; padding: 4px;
}
.legal-tabs button {
  flex: 1; padding: 10px 0; border: none; border-radius: 8px;
  font-size: 14px; font-weight: 500; font-family: inherit;
  background: transparent; color: #6b7280; cursor: pointer;
  transition: all .2s;
}
.legal-tabs button.active {
  background: #fff; color: #1e293b; box-shadow: 0 1px 4px rgba(0,0,0,.06);
}

.legal-content {
  background: #fff; border-radius: 16px; padding: 40px 36px;
  box-shadow: 0 1px 8px rgba(0,0,0,.04);
  line-height: 1.8;
}
.legal-content h1 {
  font-size: 24px; font-weight: 700; color: #0f172a;
  margin-bottom: 24px; padding-bottom: 16px; border-bottom: 1px solid #f0f0f0;
}
.legal-meta {
  font-size: 13px;
  color: #94a3b8;
  margin: -12px 0 18px;
}
.legal-submeta {
  font-size: 13px;
  color: #64748b;
  margin: -8px 0 6px;
}
.legal-owner {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 20px;
}
.legal-content h2 {
  font-size: 17px; font-weight: 600; color: #1e293b;
  margin: 28px 0 12px; padding-top: 12px;
}
.legal-content p {
  font-size: 14px; color: #4b5563; margin-bottom: 10px;
}
.legal-content ul {
  margin: 8px 0 12px 20px;
}
.legal-content li {
  font-size: 14px; color: #4b5563; margin-bottom: 6px;
}
.legal-content a {
  color: #4F6EF7; text-decoration: none;
}
.legal-content a:hover { text-decoration: underline; }

.license-lang-toggle {
  display: inline-flex; gap: 0; margin-bottom: 20px;
  border: 1px solid #e2e8f0; border-radius: 8px; overflow: hidden;
}
.license-lang-toggle button {
  padding: 7px 20px; border: none; background: #fff;
  font-size: 13px; font-weight: 500; font-family: inherit;
  color: #6b7280; cursor: pointer; transition: all .2s;
}
.license-lang-toggle button.active {
  background: #4F6EF7; color: #fff;
}
.license-lang-toggle button:not(.active):hover {
  background: #f1f5f9;
}

.license-en-notice {
  margin-bottom: 16px;
  padding: 14px 16px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #f8fafc;
}
.license-en-notice p {
  margin-bottom: 6px;
}
.license-en-notice p:last-child {
  margin-bottom: 0;
}

.license-pre {
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
  padding: 28px 24px; font-size: 12.5px; line-height: 1.7;
  font-family: "Consolas", "Monaco", "Courier New", monospace;
  color: #374151; white-space: pre-wrap; word-break: break-word;
  max-height: 70vh; overflow-y: auto;
}
</style>
