from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class FeatureStats(TypedDict):
    """
    Mathematical signature of a specific behavior for biometric analysis.

    Attributes:
        mean (float): Average value (e.g., average pixels per millisecond).
        std_dev (float): Consistency (low std_dev = very robotic/consistent).
        count (int): Number of data points used to calculate this.
        weight (float): Importance (0.0 to 1.0) of this feature for this user.
    """

    mean: float
    std_dev: float
    count: int
    weight: float


class DeviceMetadata(TypedDict):
    """
    Metadata about the user's device at the time of capture.

    Attributes:
        platform (str): Platform name (e.g., 'Win32', 'MacIntel').
        screen_res (str): Screen resolution (e.g., '1920x1080').
        browser (str): Browser name (e.g., 'Chrome', 'Edge').
        pixel_ratio (float): Device pixel ratio for coordinate normalization.
    """

    platform: str
    screen_res: str
    browser: str
    pixel_ratio: float


class BiometricProfile(BaseModel):
    """
    Main MongoDB document for a user's biometric profile.

    Attributes:
        user_id (str): Unique user identifier.
        origin_site (str): Originating website (e.g., 'bank.com', 'github.com').
        features (Dict[str, FeatureStats]): Dictionary of feature statistics.
        metadata (DeviceMetadata): Device metadata at time of capture.
        trust_score (float): Trust score for this model (increases with count).
        created_at (datetime): Timestamp when profile was created.
        last_updated (datetime): Timestamp of last update.
    """

    user_id: str = Field(..., index=True)
    origin_site: str = Field(..., index=True)
    features: Dict[str, FeatureStats]
    metadata: DeviceMetadata
    trust_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        schema_extra = {
            "example": {
                "user_id": "user_88",
                "origin_site": "myapp.com",
                "features": {
                    "mouse_velocity": {
                        "mean": 1.45,
                        "std_dev": 0.2,
                        "count": 500,
                        "weight": 1.0,
                    },
                    "key_dwell": {
                        "mean": 85.2,
                        "std_dev": 5.1,
                        "count": 120,
                        "weight": 0.8,
                    },
                },
                "trust_score": 0.85,
            }
        }


from typing import List, Optional, TypedDict, Union

from typing_extensions import Annotated


class RawInputEvent(TypedDict):
    """
    The smallest unit of data for a single movement or keypress.

    Attributes:
        t (int): Timestamp in milliseconds.
        type (str): Event type ('m' = move, 'd' = down, 'u' = up, 'kd' = keydown, 'ku' = keyup).
        x (Optional[float]): Normalized X coordinate (0.0 to 1.0).
        y (Optional[float]): Normalized Y coordinate (0.0 to 1.0).
        k (Optional[str]): Key ID (e.g., 'Shift', 'A', 'Enter'), only for non-passwords.
    """

    t: int
    type: str
    x: Optional[float]
    y: Optional[float]
    k: Optional[str]


class DeviceContext(TypedDict):
    """
    Metadata about the user's hardware at the time of capture.

    Attributes:
        sw (int): Screen width in pixels.
        sh (int): Screen height in pixels.
        dpr (float): Device pixel ratio for high-density displays.
        plt (str): Platform (e.g., 'Win32', 'MacIntel').
    """

    sw: int
    sh: int
    dpr: float
    plt: str


class BiometricPayload(TypedDict):
    """
    The full dictionary sent in the POST request body for biometric data.

    Attributes:
        user_id (str): Unique ID of the user.
        session_id (str): Unique ID for this specific interaction session.
        origin (str): The website URL (e.g., 'https://github.com').
        is_signup (bool): True if creating a new model, False for login verification.
        metadata (DeviceContext): Device context at time of capture.
        events (List[RawInputEvent]): List of raw input events.
    """

    user_id: str
    session_id: str
    origin: str
    is_signup: bool
    metadata: DeviceContext
    events: List[RawInputEvent]
